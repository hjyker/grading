import datetime
import math

from django.db.models import Count, F, Q
from rest_framework import serializers

from findiff.apps.review.constants import KPI_TYPE_MAPPINGS, MAX_RETURNED_COUNT
from findiff.apps.userprofile.models import UserProfile
from findiff.common.custom_validations import NonFieldError
from findiff.common.get_bulk_id import get_bulk_id
from findiff.models.audit import AuditOrder, QAOrder
from findiff.models.content import Book
from findiff.models.user_kpi import UserKPI


class QAOrderSerializer(serializers.ModelSerializer):
    """质检领单列表"""

    book_id = serializers.IntegerField(source='id')
    book_authors = serializers.SerializerMethodField()
    unassign_order_count = serializers.SerializerMethodField()
    unaudit_bulk_count = serializers.SerializerMethodField()
    unaudit_bulk_id = serializers.SerializerMethodField()
    qa_user = serializers.SerializerMethodField()
    qa_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'book_id', 'book_snum', 'book_name', 'book_dynasty', 'book_genre',
            'book_authors', 'unassign_order_count', 'unaudit_bulk_count',
            'unaudit_bulk_id', 'qa_user', 'qa_user_id',
        )

    def get_book_authors(self, obj):
        return [author.name for author in obj.authors.all()]

    def get_unassign_order_count(self, obj):
        return obj.article_set.filter(auditorder__order_status='2100').count()

    def get_unaudit_bulk_count(self, obj):
        return AuditOrder.objects.filter(
            order_status='2101',
            article__book=obj,
            qa_audit__qa_user=self.context['request'].user.userprofile,
        ).count()

    def get_unaudit_bulk_id(self, obj):
        unaudit_bulk = AuditOrder.objects.filter(
            order_status='2101',
            article__book=obj,
            qa_audit__qa_user=self.context['request'].user.userprofile,
        ).order_by('created_time').first()

        return unaudit_bulk.qa_audit.bulk_id if unaudit_bulk else None

    def get_qa_user(self, obj):
        audit = AuditOrder.objects.filter(
            order_status='2101', article__book=obj).first()
        if not audit:
            return None
        return getattr(
            audit.qa_audit.qa_user,
            'nickname',
            audit.qa_audit.qa_user.user.username)

    def get_qa_user_id(self, obj):
        audit = AuditOrder.objects.filter(
            order_status='2101', article__book=obj).first()
        return audit.qa_audit.qa_user.id if audit else None


class QAOrderAssignSerializer(serializers.Serializer):
    """手动分配质检领单"""

    books = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
    )
    user_id = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        audit = AuditOrder.objects.filter(
            ~Q(order_status__in=['2100', '2101']),
            article__book__in=attrs['books'],
        ).first()
        if audit:
            book_name = audit.article.book.book_name
            raise NonFieldError(f'《{book_name}》不符合分配条件')

        return attrs

    def assign_order(self):
        books = self.validated_data['books']
        user_id = self.validated_data['user_id']
        user = UserProfile.objects.get(id=user_id)
        orders = AuditOrder.objects.filter(
            article__book__in=books,
            # order_status__in=['2100', '2101'],
        )
        for order in orders:
            if not order.qa_audit:
                order.qa_audit = QAOrder.objects.create(status='unaudit')
            order.qa_audit.qa_user = user
            order.qa_audit.updated_time = datetime.datetime.now()
            order.qa_audit.operator = self.context['request'].user.userprofile
            order.qa_audit.save()

            order.updated_time = datetime.datetime.now()
            order.operator = self.context['request'].user.userprofile
            order.save()


class QAOrderApplySerializer(serializers.ModelSerializer):
    """质检领单
    质检步骤:
        1. 质检领单，按一本书籍的维度，将整个书籍关联的工单，批量创建 qa_audit 并修改对应字段数据；
        2. 抽样质检，输入抽样比例，随机将抽样工单返回审核。
    """

    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        required=True,
    )

    class Meta:
        model = Book
        fields = ['book']

    def validate(self, attrs):
        current_user = self.context['request'].user.userprofile
        exsit_unaudit = AuditOrder.objects.filter(
            order_status='2101',
            qa_audit__qa_user=current_user,
        )
        if exsit_unaudit.first():
            raise NonFieldError('请优先完成质检中的工单')

        others_order = AuditOrder.objects.filter(
            article__book=attrs['book'],
            qa_audit__isnull=False,
            qa_audit__qa_user=current_user,
        ).count()
        if others_order:
            raise NonFieldError('不能领取别人的工单')

        can_applied = AuditOrder.objects.filter(article__book=attrs['book']) \
            .values('article__book') \
            .annotate(qa_count=Count('id', filter=Q(order_status__in=['2100', '2101']))) \
            .annotate(total=Count('id')) \
            .order_by('article__book') \
            .filter(qa_count__gte=F('total'))
        if not can_applied:
            raise NonFieldError('不符合领单条件')

        return attrs

    def apply_qa_order(self):
        book = self.validated_data['book']
        orders = AuditOrder.objects.filter(
            article__book=book,
            order_status='2100',
        )

        for order in orders:
            order.qa_audit = QAOrder.objects.create(
                qa_user=self.context['request'].user.userprofile,
                status='unaudit',
            )
            order.qa_audit.serial_id = order.qa_audit.make_serial_id()
            order.qa_audit.updated_time = datetime.datetime.now()
            order.qa_audit.operator = self.context['request'].user.userprofile
            order.qa_audit.save()

            order.order_status = '2101'
            order.updated_time = datetime.datetime.now()
            order.operator = self.context['request'].user.userprofile

        AuditOrder.objects.bulk_update(
            orders,
            ['order_status', 'qa_audit', 'updated_time', 'operator'],
        )


class QAOrderSampleSerializer(serializers.ModelSerializer):
    """抽样质检
    质检步骤:
        1. 质检领单，按一本书籍的维度，将整个书籍关联的工单，批量创建 qa_audit 并修改对应字段数据；
        2. 抽样质检，输入抽样比例，随机将抽样工单返回审核。
    """

    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        required=True,
    )
    qa_ratio = serializers.IntegerField(
        required=True,
        min_value=0,
        max_value=100,
    )
    bulk_id = serializers.CharField(read_only=True)

    class Meta:
        model = AuditOrder
        fields = ['book', 'qa_ratio', 'bulk_id']

    def validate(self, attrs):
        order = AuditOrder.objects.filter(
            article__book=attrs['book'],
            qa_audit__bulk_id__isnull=False,
        ).count()
        if order:
            raise NonFieldError('不符合抽检条件')

        others_order = AuditOrder.objects.filter(
            article__book=attrs['book'],
            qa_audit__isnull=False,
            qa_audit__qa_user=self.context['request'].user.userprofile,
        ).count()
        if not others_order:
            raise NonFieldError('不能抽检别人的工单')

        return attrs

    def apply_sample(self):
        qa_ratio = self.validated_data['qa_ratio']
        book = self.validated_data['book']

        unaudit_orders = AuditOrder.objects.filter(
            article__book=book,
            order_status='2101',
            qa_audit__qa_user=self.context['request'].user.userprofile,
        )
        sample_count = math.ceil(qa_ratio / 100 * unaudit_orders.count())
        bulk_id = get_bulk_id(mix_charts=sample_count)
        sample_orders = unaudit_orders[:sample_count]
        for order in sample_orders:
            order.qa_audit.bulk_id = bulk_id
            order.qa_audit.updated_time = datetime.datetime.now()
            order.qa_audit.operator = self.context['request'].user.userprofile

            order.updated_time = datetime.datetime.now()
            order.operator = self.context['request'].user.userprofile
            order.save()

        QAOrder.objects.bulk_update(
            (od.qa_audit for od in sample_orders),
            ['bulk_id'],
        )

        self.validated_data['bulk_id'] = bulk_id


class QAOrderSubmitSerializer(serializers.Serializer):
    """质检提交"""

    book_id = serializers.CharField(
        required=True,
        write_only=True,
    )
    updated_orders = serializers.ListField(read_only=True)

    def validate(self, obj):
        # TODO 改书本下有驳回工单，不能提交
        return obj

    def save(self):
        current_user = self.context['request'].user.userprofile
        updated_time = datetime.datetime.now()

        orders = AuditOrder.objects.filter(
            article__book=self.validated_data['book_id'])
        for order in orders:
            order.order_status = '2102'
            order.updated_time = updated_time
            order.operator = current_user

            order.qa_audit.status = 'success'
            order.qa_audit.operator = current_user
            order.qa_audit.updated_time = updated_time
            order.qa_audit.save()

            order.article.content_text = order.second_audit.content_text
            order.article.article_title = order.second_audit.article_title
            order.article.article_page = order.second_audit.article_page
            order.article.author = order.second_audit.article_author
            order.article.writing_mode = order.second_audit.writing_mode
            order.article.status = 'release'
            order.article.operator = current_user
            order.article.updated_time = updated_time
            order.article.save()

        AuditOrder.objects.bulk_update(
            orders,
            ['order_status', 'updated_time', 'operator'],
        )

        kpi = []
        for order in orders:
            kpi.extend([
                UserKPI(
                    user=order.first_audit.audit_user,
                    type=KPI_TYPE_MAPPINGS.get(order.first_audit.writing_mode),
                    count=1,
                    trigger_step='qa',
                ),
                UserKPI(
                    user=order.second_audit.audit_user,
                    type=KPI_TYPE_MAPPINGS.get(order.second_audit.writing_mode),
                    count=1,
                    trigger_step='qa',
                )
            ])
        UserKPI.objects.bulk_create(kpi)

        self.validated_data['updated_orders'] = [order.id for order in orders]


class QAOrderReturnedSerializer(serializers.Serializer):
    returned_orders = serializers.PrimaryKeyRelatedField(
        queryset=AuditOrder.objects.all(),
        many=True,
        required=False,
    )
    returned_remark = serializers.CharField(required=False)
    updated_orders = serializers.ListField(read_only=True)

    def validate(self, obj):
        return obj

    def save(self):
        """处理驳回的质检工单"""

        current_user = self.context['request'].user.userprofile
        updated_time = datetime.datetime.now()

        orders = self.validated_data['returned_orders']
        for order in orders:
            order.updated_time = updated_time
            order.operator = current_user
            order.order_status = '2103'
            order.second_audit.status = 'returned'
            order.returned_count += 1
            order.returned_remark = self.validated_data['returned_remark']
            if order.returned_count > MAX_RETURNED_COUNT:
                order.returned_count = 0
                order.returned_remark = ''
                order.order_status = '1200'  # 重新放回二审领单池

                order.second_audit.audit_user = None
                order.second_audit.status = 'unassign'

                order.qa_audit.status = 'unaudit'
                order.qa_audit.updated_time = updated_time
                order.qa_audit.operator = current_user
                order.qa_audit.save()

                # 将质检人员驳回两次的数据插入绩效表
                UserKPI.objects.create(
                    user=order.second_audit.audit_user,
                    type='order_returned_shuffle',
                    count=1,
                    trigger_step='qa',
                )

            order.second_audit.updated_time = updated_time
            order.second_audit.operator = current_user
            order.second_audit.save()

        AuditOrder.objects.bulk_update(
            orders,
            ['returned_count', 'returned_remark',
             'order_status', 'updated_time', 'operator'],
        )

        self.validated_data['updated_orders'] = [order.id for order in orders]
