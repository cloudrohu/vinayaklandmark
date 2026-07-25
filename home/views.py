from django.contrib import messages

from django.shortcuts import get_object_or_404, render , redirect
from django.http import HttpResponse 
from properties.models import Property 
from utility.models import Locality,PropertyType,City,Bank
from .models import (
    Setting, Slider, Testimonial, About, Leadership,
    Contact_Page, FAQ, Our_Team,Why_Choose, ImpactMetric,Slider, Enquiry,USP,ScheduleVisit,GalleryCategory,Gallery
)
from user.models import Developer  

from django.shortcuts import render
from projects.models import Project 
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def index(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)

    project = Project.objects.filter(active=True, featured_property=True)

    settings_obj = Setting.objects.first()
    cities = City.objects.filter(level_type="CITY").order_by("name")

    residential_type = PropertyType.objects.filter(name__iexact="Residential", is_top_level=True).first()
    commercial_type = PropertyType.objects.filter(name__iexact="Commercial", is_top_level=True).first()

    residential_types = residential_type.get_descendants(include_self=True) if residential_type else PropertyType.objects.none()
    commercial_types = commercial_type.get_descendants(include_self=True) if commercial_type else PropertyType.objects.none()

    new_launch_residential = Project.objects.filter(active=True, construction_status__iexact="New Launch", propert_type__in=residential_types).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:10]

    new_launch_commercial = Project.objects.filter(active=True, construction_status__iexact="New Launch", propert_type__in=commercial_types).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:10]

    project_featured = Project.objects.filter(active=True, featured_property=True).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:6]

    featured_developers = Developer.objects.filter(featured_builder=True).order_by("-create_at")[:8]
    featured_locality = Locality.objects.filter(featured_locality=True).order_by("name")[:20]
    bank = Bank.objects.all().order_by("title")

    about_page = About.objects.filter(is_active=True).first()
    impactmetric = ImpactMetric.objects.all()
    slider = Slider.objects.first()
    why_choose_items = Why_Choose.objects.filter(is_active=True).order_by("order")
    testimonials = Testimonial.objects.all().order_by("-id")
    faqs = FAQ.objects.all().order_by("id")


    current_city = project_featured.first().city.name if project_featured.exists() else "Mumbai"

    return render(
        request,
        "home/index.html",
        {
            "menu_projects": menu_projects,
            "settings_obj": settings_obj,
            "bank": bank,
            "cities": cities,
            "current_city": current_city,
            "impactmetric": impactmetric,
            "project_featured": project_featured,
            "new_launch_residential": new_launch_residential,
            "new_launch_commercial": new_launch_commercial,
            "featured_developers": featured_developers,
            "featured_locality": featured_locality,
            "about_page": about_page,
            "why_choose_items": why_choose_items,
            "testimonials": testimonials,
            "faqs": faqs,
            "slider": slider,
            "project": project,
            "usps": USP.objects.filter(is_active=True)

        }
    )


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

        return redirect('projects:thank_you')
        


def compress_image(image):
    img = Image.open(image)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Maximum width 1920px
    img.thumbnail((1920, 1920))

    output = BytesIO()

    img.save( output, format="WEBP", quality=80, optimize=True)

    output.seek(0)

    return InMemoryUploadedFile( output, 'ImageField', os.path.splitext(image.name)[0] + ".webp", 'image/webp', output.tell(), None)

def robots_txt(request):

    robots_content = """
User-agent: *
Disallow: /admin/
Disallow: /accounts/
Allow: /

Sitemap: http://127.0.0.1:8000/sitemap.xml 
    """
    return HttpResponse(robots_content.strip(), content_type="text/plain")
    
def about_page_view(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    """
    Display the About page with:
    - About section (single)
    - Leadership list
    - Global site settings
    """

    # 🧠 Global site settings
    settings_obj = Setting.objects.filter(status="True").first()   
    about_page = About.objects.filter(is_active=True).order_by('-created_at').first()
    leaders = Leadership.objects.filter(is_active=True).order_by('display_order')

    project = Project.objects.filter(active=True, featured_property=True)\
        .prefetch_related('contact_persons')\
        .first()

    if not about_page:
        about_page = {
            "title": "About Makaan Hub",
            "subtitle": "Delivering trust, growth and innovation since 2008.",
            "projects_delivered": 120,
            "happy_families": 10000,
            "years_of_excellence": 16,
            "awards_recognitions": 12,
        }

    context = {
        "about_page": about_page,
        "leaders": leaders,
        "settings_obj": settings_obj,
        "project": project,
        "menu_projects": menu_projects,
    }
    return render(request, "home/about.html", context)

def contact_view(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    settings_obj = Setting.objects.first()
    contact_content = Contact_Page.objects.first()

    project = Project.objects.filter(
        active=True, featured_property=True
    ).prefetch_related('contact_persons').first()

    success = False

    # ✅ Show success after redirect
    if request.session.get('form_submitted'):
        success = True
        del request.session['form_submitted']

    # ✅ Handle form submit
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # 🔥 SAVE DATA
        Enquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # ✅ prevent duplicate submit
        request.session['form_submitted'] = True
        return redirect('contact')

    context = {
        "settings_obj": settings_obj,
        "contact_content": contact_content,
        "project": project,
        "success": success,
        "menu_projects": menu_projects,
    }

    return render(request, 'home/contact.html', context)

def faq_view(request):
    """Renders the FAQ page."""
    settings_obj = Setting.objects.first()

    # Fetch all FAQs (no setting filter because model doesn't have it)
    faqs = FAQ.objects.all().order_by('id')
    project = Project.objects.filter(active=True, featured_property=True).first()

    menu_projects = Project.objects.filter(active=True,featured_property=True)

    context = {
        "settings_obj": settings_obj,
        "faqs": faqs,
        "project": project,
        "menu_projects": menu_projects,
    }
    return render(request, 'home/faq.html', context)

def gallery_view(request):
    settings_obj = Setting.objects.first()
    project = Project.objects.filter(active=True, featured_property=True).first()
    menu_projects = Project.objects.filter(active=True, featured_property=True)

    categories = GalleryCategory.objects.filter(is_active=True).order_by("order")

    galleries = Gallery.objects.filter(is_active=True).select_related("category").order_by("order", "-created_at")

    context = {
        "settings_obj": settings_obj,
        "project": project,
        "menu_projects": menu_projects,

        # Gallery
        "categories": categories,
        "galleries": galleries,
    }

    return render(request, "home/gallery.html", context)

def configs_view(request):
    settings_obj = Setting.objects.first()
    project = Project.objects.filter(active=True, featured_property=True).first()

    menu_projects = Project.objects.filter(active=True,featured_property=True)

    context = {
        "settings_obj": settings_obj,
        "project": project,
        "menu_projects": menu_projects,
    }
    return render(request, 'home/configurations.html', context)

def amenities_view(request):
    settings_obj = Setting.objects.first()
    project = Project.objects.filter(active=True, featured_property=True).first()

    menu_projects = Project.objects.filter(active=True,featured_property=True)

    context = {
        "settings_obj": settings_obj,
        "project": project,
        "menu_projects": menu_projects,
    }
    return render(request, 'home/amenities.html', context)

def submit_home_enquiry(request):
    if request.method == "POST":

        Enquiry.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )

        messages.success(request, "Enquiry submitted successfully.")

        return redirect("thank_you")      # ya "projects:thank_you"

    return redirect("home")

#-----------------------------------------------------------------------------------------------

def get_setting():

    menu_projects = Project.objects.filter(active=True,featured_property=True)
    
    settings_obj = Setting.objects.filter(status="True").first()    

    return Setting.objects.first()

def privacy_policy(request):

    menu_projects = Project.objects.filter(active=True,featured_property=True)
    settings_obj = Setting.objects.filter(status="True").first()    
    context = {
        "settings_obj": settings_obj,
        "menu_projects": menu_projects,
    }

    return render(request, 'terms/privacy_policy.html', context)

def terms_conditions(request):
    settings_obj = Setting.objects.filter(status="True").first()   

    menu_projects = Project.objects.filter(active=True,featured_property=True)
    context = {
        "settings_obj": settings_obj,
        "menu_projects": menu_projects,
    }
    return render(request, 'terms/terms_conditions.html', context)

def disclaimer(request):
    settings_obj = Setting.objects.filter(status="True").first()    
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    context = {
        "settings_obj": settings_obj,
        "menu_projects": menu_projects,
    }
    return render(request, 'terms/disclaimer.html', context)

def cookies(request):
    settings_obj = Setting.objects.filter(status="True").first()    
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    context = {
        "settings_obj": settings_obj,
        "menu_projects": menu_projects,
    }
    return render(request, 'terms/cookies-policy.html', context)

def calculator(request):
    menu_projects = Project.objects.filter(active=True,featured_property=True)
    settings_obj = Setting.objects.filter(status="True").first()    

    context = {
        "settings_obj": settings_obj,
        "menu_projects": menu_projects,
    }
    return render(request, 'home/calculator.html', context)

def schedule_visit(request):
    if request.method == "POST":
        ScheduleVisit.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            visit_date=request.POST.get("date"),
            visit_time=request.POST.get("time"),
        )

        return redirect("/projects/thank-you/")

    return redirect("/")