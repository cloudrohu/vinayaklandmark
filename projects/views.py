# projects/views.py
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q 
from .models import Project
from home.models import Setting
from properties.models import Property # Needed for project_details if included
# Import related models for dropdowns
from utility.models import City, Locality , PropertyType , PossessionIn , ProjectAmenities , Bank , PropertyAmenities
# Import related models for dropdowns
from .models import (
    Project, Configuration, Gallery, RERA_Info, BookingOffer, Overview,
    USP, Amenities, Header, WelcomeTo, Connectivity, WhyInvest,Enquiry,ProjectFAQ
) 
import os
from io import BytesIO
from django.http import FileResponse
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Image,Spacer,)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Min, Max

def index(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    # Start with all active projects
    queryset_list = Project.objects.filter(active=True).order_by('project_name')

    
    if 'city_id' in request.GET and request.GET['city_id']:
        city_id = request.GET['city_id']
        queryset_list = queryset_list.filter(city_id=city_id)

    if 'locality_id' in request.GET and request.GET['locality_id']:
        locality_id = request.GET['locality_id']
        try:
            # Get the selected Locality node (e.g., Phase 1)
            selected_locality = Locality.objects.get(pk=locality_id)
            
            # Fetch all descendants (sub-localities) including the node itself
            descendant_localities = selected_locality.get_descendants(include_self=True)
            
            # Filter projects whose locality FK is within the fetched MPTT tree
            queryset_list = queryset_list.filter(locality__in=descendant_localities)
            
        except Locality.DoesNotExist:
            pass # Ignore if invalid ID is passed


    if 'status' in request.GET and request.GET['status']:
        status = request.GET['status']
        queryset_list = queryset_list.filter(construction_status__iexact=status)

    if 'keywords' in request.GET and request.GET['keywords']:
        keywords = request.GET['keywords']
        queryset_list = queryset_list.filter(
            Q(project_name__icontains=keywords) | 
            Q(developer__name__icontains=keywords)
        )
        
    
    available_cities = City.objects.all().order_by('name')
    # Fetch all *top-level* Localities for the main dropdown (or all of them if preferred)
    available_localities = Locality.objects.filter(parent__isnull=True).order_by('name')
    construction_statuses = Project.Construction_Status
    
    context = {
        "menu_projects": menu_projects,
        'projects': queryset_list,
        'available_cities': available_cities,
        'available_localities': available_localities,
        'construction_statuses': construction_statuses,
        'values': request.GET, # Passes submitted values back to the form
    }
    
    return render(request, 'projects/projects.html', context)

def search_projects(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    settings_obj = Setting.objects.first()

    # ================= SAFE GET PARAMS =================
    location  = request.GET.get("q", "").strip()
    bhk       = request.GET.get("bhk")
    area      = request.GET.get("area")
    amenities = request.GET.get("amenities")
    sort      = request.GET.get("sort")

    # ================= BASE QUERY =================
    projects = Project.objects.filter(active=True)

    # ================= SEARCH (LOCATION FIRST) =================
    if location:
        location = location.split(",")[0].strip()

        projects = projects.filter(
            Q(project_name__icontains=location) |
            Q(locality__name__icontains=location)
        )

    # ================= BHK (EXISTS – NO PROJECT DROP) =================
    if bhk:
        bhk_qs = ProjectConfiguration.objects.filter(
            project=OuterRef("pk"),
            bhk_type=bhk
        )
        projects = projects.annotate(
            has_bhk=Exists(bhk_qs)
        ).filter(has_bhk=True)

    # ================= AREA (EXISTS) =================
    if area:
        area_qs = ProjectConfiguration.objects.filter(
            project=OuterRef("pk"),
            area_sqft__gte=int(area)
        )
        projects = projects.annotate(
            has_area=Exists(area_qs)
        ).filter(has_area=True)

    # ================= AMENITIES (EXISTS) =================
    if amenities:
        amenity_list = [a.strip() for a in amenities.split(",") if a]

        amenity_qs = ProjectAmenities.objects.filter(
            project=OuterRef("pk"),
            name__in=amenity_list
        )
        projects = projects.annotate(
            has_amenity=Exists(amenity_qs)
        ).filter(has_amenity=True)

    # ================= PRICE =================
    projects = projects.annotate(
        min_price=Min("configurations__price_in_rupees")
    )

    # ================= SORT =================
    if sort == "price_low":
        projects = projects.order_by("min_price")
    elif sort == "price_high":
        projects = projects.order_by("-min_price")
    else:
        projects = projects.order_by("-create_at")

    # ================= PAGINATION =================
    paginator = Paginator(projects, 9)
    projects_page = paginator.get_page(request.GET.get("page"))

    # ================= AJAX =================
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "projects/_project_results.html",
            {"projects": projects_page},
            request=request
        )
        return JsonResponse({"html": html})

    return render(request, "projects/residential_list.html", {
        "projects": projects_page,
        "menu_projects": menu_projects,
        "settings_obj": settings_obj,
        "selected": request.GET,
    })

def residential_projects(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    
    query = request.GET.get("q", "")  # YES
    bhk = request.GET.get("bhk")      # YES
    min_price = request.GET.get("min_price")  # YES
    max_price = request.GET.get("max_price")  # YES

    projects = Project.objects.filter(
        propert_type__parent__name__iexact="Residential",
        active=True
    ).annotate(
        min_price=Min("configurations__price_in_rupees"),
        max_price=Max("configurations__price_in_rupees"),
    ).select_related(
        "city", "locality", "propert_type"
    )  # YES

    if query:
        projects = projects.filter(project_name__icontains=query)  # YES

    if bhk:
        projects = projects.filter(
            configurations__bhk_type__icontains=bhk
        )  # UPDATED (dynamic bhk)

    if min_price:
        projects = projects.filter(
            max_price__gte=min_price
        )  # UPDATED (overlap logic)

    if max_price:
        projects = projects.filter(
            min_price__lte=max_price
        )  # UPDATED (overlap logic)

    context = {
        "projects": projects.distinct(),  # YES
        "page_title": "Residential Projects",  # YES
        "breadcrumb": "Residential",  # YES
        "menu_projects": menu_projects,

    }

    return render(request, "projects/residential_list.html", context)  # YES

def project_details(request, id, slug):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    # ================= CURRENT PROJECT CARPET =================
    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft")
    )

    # ================= RELATED PROJECTS (SAME LOCALITY) =================
    related_projects = (
            Project.objects
            .filter(active=True)
            .exclude(id=project.id)
            .filter(
                Q(locality=project.locality) |      # same locality
                Q(city=project.city) |              # same city
                Q(developer=project.developer)      # same developer
            )
            .annotate(
                min_carpet=Min("configurations__area_sqft"),
                max_carpet=Max("configurations__area_sqft"),
                min_price=Min("configurations__price_in_rupees"),
            )
            .select_related("city", "locality", "developer")
            .prefetch_related("configurations")
            .distinct()[:8]
        )
    # ================= FALLBACK → SAME CITY =================
    if not related_projects.exists():
        related_projects = (
            Project.objects
            .filter(active=True, city=project.city)
            .exclude(id=project.id)
            .annotate(
                min_carpet=Min("configurations__area_sqft"),
                max_carpet=Max("configurations__area_sqft"),
                min_price=Min("configurations__price_in_rupees"),
            )
        )

    related_projects = related_projects[:8]


    bank = Bank.objects.all()
    print("Bank Count:", bank.count())


    context = {
        "menu_projects": menu_projects,
        "project": project,
        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],
        "related_projects": related_projects,
        "project_faqs": project.faqs.all().order_by("order"),
        "menu_projects": menu_projects,
        "bank": bank,


    }

    return render(request, "projects/project_detail.html", context)


# 🏢 Commercial Projects
def commercial_projects(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    query = request.GET.get('q', '')
    projects = Project.objects.filter(
        propert_type__parent__name__iexact='Commercial',
        active=True
    ).select_related('city', 'locality', 'propert_type')

    if query:
        projects = projects.filter(project_name__icontains=query)

    context = {
        'projects': projects,
        'page_title': 'Commercial Projects',
        'breadcrumb': 'Commercial',
        "menu_projects": menu_projects,

    }
    return render(request, 'projects/commercial_list.html', context)

def project_details(request, id, slug):
    menu_projects = Project.objects.filter(active=True,featured_property=True)

    # ✅ STEP 1: FETCH PROJECT FIRST
    project = get_object_or_404(Project, id=id, slug=slug, active=True)

    # ✅ STEP 2: SETTINGS
    settings_obj = Setting.objects.first()
    rs = Setting.objects.first()

    # ✅ STEP 3: CARPET RANGE
    carpet_range = project.configurations.aggregate(
        min_area=Min("area_sqft"),
        max_area=Max("area_sqft")
    )

    # ✅ STEP 4: RELATED PROJECTS (LOCALITY FIRST)
    related_projects = Project.objects.filter(
        locality=project.locality,
        active=True
    ).exclude(id=project.id)

    # 👉 Fallback: agar same locality me aur project na mile
    if not related_projects.exists():
        related_projects = Project.objects.filter(
            city=project.city,
            active=True
        ).exclude(id=project.id)

    related_projects = related_projects[:8]

    # ✅ STEP 5: FAQ
    project_faqs = project.faqs.all().order_by("order")

    # ✅ STEP 6: FINAL CONTEXT
    context = {
        "project": project,
        "active": project,

        "settings_obj": settings_obj,
        "rs": rs,

        "min_carpet": carpet_range["min_area"],
        "max_carpet": carpet_range["max_area"],

        "welcome": project.welcomes.all(),
        "usps": project.usps.all(),
        "configurations": project.configurations.all().order_by("bhk_type"),
        "gallery": project.gallery.all(),
        "amenities": project.amenities.all(),
        "rera": project.rera.all(),
        "BookingOffer": project.BookingOffer.all(),
        "headers": project.headers.all(),
        "configs": project.configurations.all(),
        "why_invest": project.why_invest.all(),

        # ✅ RELATED + FAQ
        "project_faqs": project_faqs,
        "related_projects": related_projects,

        # OPTIONAL
        "properties": Property.objects.filter(project=project),
        "menu_projects": menu_projects,

    }

    return render(request, "projects/project_detail.html", context)

def submit_enquiry(request, id):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    project = get_object_or_404(Project, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Save enquiry
        Enquiry.objects.create(
            project=project,
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        
        context = {
            "project": project,          # current project
            "menu_projects": menu_projects,
        }

        messages.success(request, "Thank you! Your enquiry has been submitted successfully.")
        return redirect('thank_you')  # or use project detail slug redirect

    return redirect('project_details', id=project.id, slug=project.slug, context=context)


def thank_you(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)

    context = {
        "menu_projects": menu_projects,
    }

    return render(request, 'projects/thank_you.html', context)


def load_localities(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    city_id = request.GET.get("city_id")
    localities = Locality.objects.filter(city_id=city_id).values("id", "name")
   
    context = {
        "menu_projects": menu_projects,
    }

    return JsonResponse(list(localities), safe=False,context=context)



def configuration_pdf(request, id):

    try:
        config = Configuration.objects.select_related("Project").get(pk=id)
    except Configuration.DoesNotExist:
        raise Http404("Configuration not found")

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>PROJECT DETAILS</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(f"<b>Project :</b> {config.Project.project_name}", styles["Normal"])
    )

    story.append(
        Paragraph(f"<b>BHK :</b> {config.bhk_type}", styles["Normal"])
    )

    story.append(
        Paragraph(f"<b>Area :</b> {config.area_sqft} Sq.ft", styles["Normal"])
    )

    story.append(
        Paragraph(f"<b>Price :</b> {config.formatted_price()}", styles["Normal"])
    )

    story.append(Spacer(1,20))

    if config.unit_plan and os.path.exists(config.unit_plan.path):

        img = Image(config.unit_plan.path)

        img.drawWidth = 6 * inch
        img.drawHeight = 4 * inch

        story.append(img)

    doc.build(story)

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"{config.Project.project_name}.pdf",
    )