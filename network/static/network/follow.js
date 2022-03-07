const button = document.querySelector("button"); 
const user_id = parseInt(document.getElementById("user").innerHTML); 

button.addEventListener('click', function() {
    if (this.innerHTML === "Follow") 
    {
        // send a POST request that says user wants to follow the user with the id of user_id 
        fetch(`/handle_follow`, {
            method: 'POST',
            body: JSON.stringify({
                user_id: user_id,     
                follow: true   
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.message === "Success")
            {
                // Followed      
                this.innerHTML = "Unfollow"; 

                // update number of followers    
                document.getElementById("number_of_followers").innerHTML = `Number of followers: ${result.number_of_followers}`; 
            }
        });
    }
    else
    {
        // send a POST request that says user wants to unfollow the user with the id of user_id  
        fetch(`/handle_follow`, {
            method: 'POST',
            body: JSON.stringify({
                user_id: user_id,  
                follow: false     
            })
        })
        .then(response => response.json())
        .then(result => { 
            if (result.message === "Success")
            {
                // Unfollowed    
                this.innerHTML = "Follow"; 

                // update number of followers 
                document.getElementById("number_of_followers").innerHTML = `Number of followers: ${result.number_of_followers}`; 
            }
        });
    }
});

