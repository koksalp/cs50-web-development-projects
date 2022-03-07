const edits = document.querySelectorAll('.edit'); 

edits.forEach(element => {

    element.addEventListener('click', () => {

        // initialize all necessary variables 
        const post_id = parseInt(element.parentElement.lastElementChild.innerHTML);  
        let content_element = element.previousElementSibling; 
        const content = content_element.innerHTML; 
        const div = element.parentElement; 
        const elements = edit_elements(content); 
        const save_button = elements["save_button"];  
        const text_area = elements["text_area"]; 

        // replace elements  
        div.replaceChild(save_button, element); 
        div.replaceChild(text_area, content_element);   

        save_button.addEventListener('click', () => {

            // editted text 
            new_text = text_area.value; 

            // send a PUT request to update the text content   
            fetch(`/posts/${post_id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    content: new_text             
                })
            })

            // replace old elements with new ones 
            div.replaceChild(element, save_button); 
            div.replaceChild(content_element, text_area);   

            // update content without reloading the page   
            content_element.innerHTML = new_text; 
        })
    }); 
}); 

// create and return text area and save button 
function edit_elements(content)    
{
    const save_button = document.createElement("button"); 
    save_button.type = "button"; 
    save_button.innerHTML = "Save"; 
    const text_area = document.createElement("textarea"); 
    text_area.innerHTML=content;    
    text_area.name = "new_post"; 
    return {
        "save_button": save_button, 
        "text_area": text_area
    };
} 