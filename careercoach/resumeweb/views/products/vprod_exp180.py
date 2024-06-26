import os
from zzz_lib.zzz_log import zzz_print
import json
from django.db.models import Q
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.conf import settings
from django.shortcuts import get_list_or_404, get_object_or_404

from ...models import (
    mprod_exp180,
    mprod_exp180_catlist,
    mprod_intprep,
    mprod_intprep_catlist,
    mprod_proflevel_list,
    mprod_proflevel,
    mprod_proglang_list,
    mprod_proglang,
    mprod_rolebased_list,
    mprod_rolebased,
    mprod_strategy_taglist,
    mprod_strategy,
    mprod_visabased_list,
    mprod_visabased,
)

from ..rw_cart_detailview import (
    cartDetailView_byMode,
    cartDetailViewClass
)

from ...data_prod_comp_v3 import (
    prod_comp_data_exp180,

)

from ...product_selection import (
    generate_product_list,
)

from resumeweb.product_selection import fetchExp180Randomly

from cloudops.fetch_data import (
    fetch_data_faq,
    fetch_data_ta,
    fetch_data_impfact
)

from ...fetch_product_data import (
    get_category,
    get_cat_list,
    get_other_services,
)

PATH_PRODUCT_LAYOUT     = "resumeweb/layout/products/1-exp180/"
PATH_ROOT               = os.path.join(settings.BASE_DIR)
PATH_PRODUCT_COMPONENT  = 'resumeweb/templates/resumeweb/components/products/exp180'

PRODUCT_LINE        = 'exp180'
PRODUCT_SLOGAN      = 'add slogan hereidentity'
MODEL_PRODUCT       = mprod_exp180
MODEL_PRODUCT_CAT   = mprod_exp180_catlist


# ******************************************************************************
class Exp180Home(ListView):
    template_name = PATH_PRODUCT_LAYOUT + "homepg.html"
    model = MODEL_PRODUCT

    def get_queryset(self):
        qs1 = super().get_queryset()
        qs1 = qs1.order_by('category')
        return qs1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['product_line'] = PRODUCT_LINE
        context['ta_list'] = fetch_data_ta(PRODUCT_LINE)
        context['pg_layout_type'] = 'homepg'

        return context


# ******************************************************************************
class Exp180ServiceAll(ListView):
    template_name = PATH_PRODUCT_LAYOUT + "all_serv.html"
    model = MODEL_PRODUCT

    def get_queryset(self):
        qs1 = super().get_queryset()
        qs1 = qs1.order_by('category')
        return qs1

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        ## special items
        # cat list section
        context['cat_list'] = MODEL_PRODUCT_CAT.objects.values_list('catname', flat=True).distinct()

        ## left sidebar items
        context['all_serv_link'] = True
        context['prod_ins_menu'] = True
        context['need_help'] = True
        context['need_customization'] = True

        ## common items
        context['product_line'] = PRODUCT_LINE
        context['pg_header'] = 'All Services'
        context['pg_layout_type'] = 'all_serv_list'

        return context


# by cat 
# ******************************************************************************
class Exp180ServiceBycat(ListView):
    template_name = PATH_PRODUCT_LAYOUT + "all_serv.html"
    model = MODEL_PRODUCT

    def get_queryset(self):
        qs1 = super().get_queryset()
        category_selected = get_object_or_404(MODEL_PRODUCT_CAT, catname=self.kwargs.get('category'))
        qs1 = qs1.filter(category=category_selected)
        return qs1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # cat_list / by_cat related info    
        category_selected = self.kwargs['category']    
        cat_list = MODEL_PRODUCT_CAT.objects.all()

        # product, product page info
        # this section is common in all strategy solution product pages
        context['category_selected'] = category_selected
        context['cat_list'] = cat_list
        
        # left sidebar items
        context['all_serv_link'] = True
        context['prod_ins_menu'] = True
        context['need_help'] = True
        context['need_customization'] = True

        ## common items
        context['product_line'] = PRODUCT_LINE
        context['pg_header'] = 'Services by Category'
        context['pg_layout_type'] = 'all_serv_list'

        return context


# ******************************************************************************
def populate_cardDetailViewClass():
    product_model_name              = "mprod_exp180"
    product_detail_template_name    = "resumeweb/pg-contents/product-details-v2/prod-details.html"
    breadcrumb_url_name             = "exp180_services_all"     # Name of django view that is used for breadcrumb url for this product
    breadcrumb_url_displaytext      = "All Exp180 Services"     # Text to display in breadcrumb url
    return cartDetailViewClass(product_model_name, product_detail_template_name, breadcrumb_url_name, breadcrumb_url_displaytext)


# ******************************************************************************
def Exp180DetailView_ajax(request, id):
    zzz_print("    %-28s: %s" % ("Exp180DetailView_ajax (id)", id))
    icdvc = populate_cardDetailViewClass()
    html  = cartDetailView_byMode(request, icdvc, id, "ajax")
    # zzz_print("    %-28s: %s" % ("html", html))
    return html


# ******************************************************************************
def Exp180DetailView(request, id):
    zzz_print("    %-28s: %s" % ("Exp180DetailView (id)", id))
    full_template                   = loader.get_template(PATH_PRODUCT_LAYOUT+'prod-details.html')

    icdvc = populate_cardDetailViewClass()
    html  = cartDetailView_byMode(request, icdvc, id, "html")
    # zzz_print("    %-28s: %s" % ("html", html))

    cat_selected = get_category(id,MODEL_PRODUCT,MODEL_PRODUCT_CAT)
    # print(MODEL_PRODUCT)
    cat_list = get_cat_list(id,MODEL_PRODUCT,MODEL_PRODUCT_CAT)
    other_services = get_other_services(id,MODEL_PRODUCT)

    context = {
        'mmh_product_details_contents': html,

        # right column items
        'cat_list': cat_list,
        'cat_selected': cat_selected,
        'serv_others': other_services,
        
        # common items
        'product_line'      : PRODUCT_LINE,
        'pg_header'         : 'Product Details',
        'questions_answers' : fetch_data_faq(PRODUCT_LINE),
        'ta_list'           : fetch_data_ta(PRODUCT_LINE),
        'fa_list'           : fetch_data_impfact(PRODUCT_LINE)
    }
    return HttpResponse(full_template.render(context, request))


# how it works
# ******************************************************************************
class Exp180HowItWorks(TemplateView):
    template_name = PATH_PRODUCT_LAYOUT + "prod_ins_pg.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'product_line': PRODUCT_LINE,
            'prod_slogan': PRODUCT_SLOGAN,
            'common_items': True,

            'pg_header': 'How it works',
            'how_it_works_section': True
        }
        return context


# Product Comparison
# ******************************************************************************
class Exp180CompareThis(TemplateView):
    template_name = "resumeweb/layout/base_prod_comparison_v2.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        prod_comp_data = [i[1] for i in prod_comp_data_exp180]
        prod_list_others = generate_product_list(PRODUCT_LINE)

        context = {
            'prod_comp_data': prod_comp_data,
            'prod_list_others': prod_list_others,
            'product_line': PRODUCT_LINE,
            'prod_slogan': PRODUCT_SLOGAN,
            'common_items': True,

            'pg_header': 'Product Comparison',
            'prod_comp_section': True,

        } 
        return context


# use cases
# ******************************************************************************
class Exp180UseCases(TemplateView):
    template_name = PATH_PRODUCT_LAYOUT + "prod_ins_pg.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'product_line': PRODUCT_LINE,
            'prod_slogan': PRODUCT_SLOGAN,
            'common_items': True,

            'ta_list': fetch_data_ta(PRODUCT_LINE),
            'pg_header': 'Use Cases',
            'use_cases_section': True,
        } 
        return context


# deliver method
# ******************************************************************************
class Exp180ProductDeliveryMethods(TemplateView):
    template_name = PATH_PRODUCT_LAYOUT + "prod_ins_pg.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'product_line': PRODUCT_LINE,
            'prod_slogan': PRODUCT_SLOGAN,
            'common_items': True,

            'pg_header'         : 'Product Delivery Methods',
            'gen_pdm_section'   : True,
            'ta_list'           : fetch_data_ta(PRODUCT_LINE),
        }
        return context 


# product faq
# ******************************************************************************
class Exp180FAQ(TemplateView):
    template_name = PATH_PRODUCT_LAYOUT + "prod_ins_pg.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'product_line': PRODUCT_LINE,
            'prod_slogan': PRODUCT_SLOGAN,
            'common_items': True,

            'pg_header': 'FAQs',
            'exp180_faq_section': True,
            'questions_answers': fetch_data_faq(PRODUCT_LINE)
        }

        return context
