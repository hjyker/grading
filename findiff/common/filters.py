from django_filters.filters import (BaseInFilter, BaseRangeFilter,
                                    CharFilter, DateTimeFilter)


class DateTimeRangeFilter(BaseRangeFilter, DateTimeFilter):
    """实现接口传递: A,B 格式的时间区间"""
    pass


class ChartInFilter(BaseInFilter, CharFilter):
    pass
