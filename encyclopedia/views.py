from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from django import forms
from django.urls import reverse
import markdown2
from random import randint

class newEntry(forms.Form):
    title = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Title', 'size': '50', 'autocomplete': 'off'}))
    entry = forms.CharField(label="", widget=forms.Textarea(attrs={'rows': '5', 'cols': '10'}))

def index(request):
    if request.method == "POST":
        search = request.POST["q"]
        possible_entries = []

        # iterate through titles and redirect user to the entry's page if there is a match 
        for entry in util.list_entries():
            if search.lower() == entry.lower():
                return HttpResponseRedirect("wiki/{}".format(entry))
            if entry.lower().find(search.lower()) != -1 or search.lower().find(entry.lower()) != -1:
                possible_entries.append(entry)                
        
        # display index.html with a list of all titles of possible entries 
        # and indicate that index page is now used for listing search results in order to avoid having one more route for results 
        return render(request, "encyclopedia/index.html", {
            "entries": possible_entries,
            "result": "search"
        })

    # if method is get, list all titles 
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "result": "index"
    })
    
def createNewPage(request):
    if request.method == "POST":
        form = newEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]

            # if title is already exist, display an error message
            if title.lower() in [i.lower() for i in util.list_entries()]:      
                return render(request, "encyclopedia/error.html", {
                    "status": "already exists"
                })
            
            # if title is not exist, save the entry and redirect user to the new entry's page
            util.save_entry(title, entry)
            return HttpResponseRedirect("wiki/{}".format(title))
        
        # if form is not valid, show the same form with the same content
        else:
            return render(request, "encyclopedia/create_new_page.html", {
                "form": form            
                })

    # if the method is get, display an empty form 
    return render(request, "encyclopedia/create_new_page.html", {
        "form": newEntry() 
    })

def display(request, title):
    if request.method == "POST":         
    
        # if user clicks on edit button, display edit.html with existing content  
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "html": util.get_entry(title)
        }) 
    
    # if title is not exist, display an error message 
    if not util.get_entry(title):      
        return render(request, "encyclopedia/error.html", {
            "status": "not found"
        })
   
    # if title is exist, display its content
    return render(request, "encyclopedia/entry.html", {
        "html": markdown2.markdown(util.get_entry(title)),
        "title": title
    })  

# function to display random entry
def random(request):
    entries = util.list_entries()
    length = len(entries)
    return HttpResponseRedirect("wiki/{}".format(entries[randint(0, length - 1)]))

def edit(request):
    if request.method == "POST":        
        context = request.POST
        original_title, changed_title, textarea = context["hidden"], context["title"], context["textarea"]          
        
        # if new title is exist, display an error message via error.html 
        if changed_title.lower() in [i.lower() for i in util.list_entries()] and changed_title.lower() != original_title.lower():
            return render(request, "encyclopedia/error.html", {
                    "status": "already exists"
                })
                
        # delete original entry
        util.delete_entry(original_title)
        
        # save new entry 
        util.save_entry(changed_title, textarea)
        
        return HttpResponseRedirect("wiki/{}".format(changed_title))
    
    # if the method is get, redirect user to main page 
    return HttpResponseRedirect(reverse("index"), {
        "result": "index"
    })