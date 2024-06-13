from django_filters import rest_framework as filters
from reviews.models import Title


class TitleRangeFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug",
                                  lookup_expr='contains')
    genre = filters.CharFilter(field_name="genre__slug",
                               lookup_expr='contains')
    name = filters.CharFilter(field_name="name",
                              lookup_expr='contains')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']
