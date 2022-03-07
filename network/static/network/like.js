const likes = document.querySelectorAll('i');   
const current_user_class = document.querySelector(".current_user_class"); 
let is_anonim; 

// check if the user is authenticated    
if (current_user_class === null)
{
    is_anonim = false; 
}
else
{
    is_anonim = current_user_class.innerHTML === "AnonymousUser" ? true : false ;  
}  

likes.forEach(element => {

    element.addEventListener('click', () => { 

        if (is_anonim)
        {
            alert("You should login in order to like a post."); 
        }
        else
        {
            // initialize all necessary variables  
            const post_id = parseInt(element.parentElement.nextElementSibling.innerHTML); 
            const post_likes = element.parentElement.childNodes[2];  
            let number_of_likes;  
            let like_color = ""; 

            // send a GET request to get number of likes      
            fetch(`/posts/${post_id}`)
            .then(response => response.json())
            .then(post => {
                number_of_likes = parseInt(post.number_of_likes); 
            }).then(() => {
                if (element.style.color == "white")
                {   
                    
                    // send a PUT request to update number of likes 
                    fetch(`/posts/${post_id}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            number_of_likes: number_of_likes + 1
                        })
                    })
                    number_of_likes++; 
                    like_color = "red"; 
                }
                else
                {
                    fetch(`/posts/${post_id}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            number_of_likes: number_of_likes - 1 
                        })
                    })          
                    number_of_likes--;  
                    like_color = "white"; 
                }
            }).then(() => {
                post_likes.textContent = number_of_likes;  
                element.style.color = like_color;  
            }).then(() => {

                // decide whethher user liked or unliked post 
                let like_or_unlike = element.style.color == "red"  ? true : false  ; 
     
                // send a POST request to indicate whether user liked a post or not 
                fetch(`/posts/${post_id}`, {
                    method: 'POST',
                    body: JSON.stringify({
                      like: like_or_unlike  
                    })
                  })
                  .then(response => response.json())
                  .then(result => {
                      // Print result
                      console.log(result);
                  });
            });
        }

    }); 
}); 
