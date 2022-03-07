document.addEventListener('DOMContentLoaded', function() {         

    // select form element  
    const form = document.getElementById("compose-form"); 

    // send email when form is submitted   
    form.onsubmit = function() {

        // get users data and store them 
        const recipients = document.getElementById("compose-recipients").value; 
        const subject = document.getElementById("compose-subject").value;
        const body = document.getElementById("compose-body").value;
        
        // send email via fetch using post request 
        fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: body 
            })
        })
        .then(response => response.json())
        .then(result => {
            
            // load user's sent mailbox   
            load_mailbox("sent");
        });

        // return false in order not to load user's inbox 
        return false ; 
    }

    // By default, load the inbox
    load_mailbox('inbox');
    
    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', () => compose_email(false));
});

// function to compose email and set default values so that this can be used to reply emails 
function compose_email(reply=false, recipients="", subject="", timestamp="", body="" ) {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';     
    document.querySelector("#show-emails").style.display = "none"; 

    // select elements 
    const composeRecipients = document.querySelector('#compose-recipients');
    const composeSubject = document.querySelector('#compose-subject');
    const composeBody = document.querySelector('#compose-body');

    // this part is executed if user wants to reply 
    if (reply)
    {
        // pre-fill the recipient, subject and body 
        composeRecipients.value = recipients; 
        composeSubject.value = subject.startsWith('Re: ') ? subject : 'Re: '+ subject;
        composeBody.value = `On ${timestamp} ${recipients} wrote: ` + body; 
    }

    // this part is executed when user wants to send email but not reply      
    else
    {
    // Clear out composition fields 
    composeRecipients.value = '';
    composeSubject.value = '';
    composeBody.value = '';

    }
}

function load_mailbox(mailbox) {
    
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none'; 
    document.querySelector("#show-emails").style.display = "none";
    
    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // select the div called emails-view    
    const emailView = document.getElementById("emails-view");
    
    // send a GET request to retrieve data 
    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(data => { 
        
        // iterate over data and show them to user properly   
        for (let i = 0; i < data.length; i++)
        {
            // create a div for each mail 
            const new_div = document.createElement("div");        

            // use ternary operator to choose one of the options 
            let from_or_to = mailbox === "inbox" || mailbox === "archive" ? "From" : "To";  
            let sender_or_receiver = mailbox === "inbox" || mailbox === "archive" ? "sender" : "recipients";  
            
            // create p elements for sender, recepients, subject and timestamp info 
            const create_from = document.createElement("p");
            create_from.innerHTML = from_or_to + ": " + data[i][sender_or_receiver];
            
            const create_subject = document.createElement("p");
            create_subject.innerHTML = "Subject: " + data[i]["subject"]; 
            
            const create_timestamp = document.createElement("p");
            create_timestamp.innerHTML = "Timestamp: " + data[i]["timestamp"]; 

            // append each p elements to new_div element             
            [create_from, create_subject, create_timestamp ].forEach(element => {
                new_div.appendChild(element);
            });             

            // this part is executed if mailbox is inbox or archieve 
            if (mailbox === "inbox" || mailbox === "archive")
            {
                // use ternary operator to assign value depending on whether mailbox is inbox or not 
                const is_inbox = mailbox === "inbox" ? true : false; 

                // create a button for archive     
                const archive_button = document.createElement("button");

                // give button a class 
                archive_button.className = "email-button";

                
                // append archive button to div so that each mail has the ability to archive or unarchive       
                new_div.appendChild(archive_button);

                // if mailbox is inbox the button is used for archive
                // else the button is used for unarchive which means mailbox is archive and email is already archived         
                archive_button.innerHTML = is_inbox ? "Archive" : "Unarchive";    
                
                // if mailbox is inbox 
                if (is_inbox)
                {                
                    // when archive button is clicked, send a PUT request to change archived info to true meaning this specific email is now archived   
                    // after the process is over remove the div and load inbox  
                    archive_button.onclick = function() { 
                        fetch(`/emails/${data[i]["id"]}`, {
                            method: 'PUT',
                            body: JSON.stringify({
                                archived: true
                            })
                        })
                        .then(() => {
                            new_div.remove();
                            load_mailbox("inbox"); 
                        }); 
                        
                    }
                }

                // if mailbox is archive      
                else 
                {
                    // when button is clicked send a PUT request to change info for archived    
                    // to false meaning this email is now unarchived and after the process is over load inbox 
                    archive_button.onclick = function() { 
                        fetch(`/emails/${data[i]["id"]}`, {
                            method: 'PUT',
                            body: JSON.stringify({
                                archived: false
                            })
                        })
                        .then(() => {
                            load_mailbox("inbox"); 
                        });
                    } 
                }
            }
            // set new_div's classname to email 
            new_div.className = "email"; 

            // decide whether email is read or not 
            const read = data[i]["read"] ? "read" : "unread"; 

            // add read as classname to new_div so that different classname is added based on whether email is read or not 
            new_div.classList.add(read);
      
            // append new_div element to emailView  
            if (!((data[i]["archived"]) && mailbox === "inbox" ))
            {
                emailView.appendChild(new_div);            
            }
                            
            // add event listener to new_div so that everytime it gets clicked the following function will be called 
            new_div.onclick = function(event) {
                
                // load message unless archive   or unarchive button is clicked 
                if (event.target.innerHTML !== "Archive" && event.target.innerHTML !== "Unarchive")
                {
                load_message(data[i]["sender"], data[i]["recipients"], data[i]["subject"], data[i]["timestamp"], data[i]["body"] , data[i]["id"]);
                }
            }
        }
    });
}
// function to load message    
function load_message(sender, recipients, subject, timestamp, body, email_id)
{
    // Hide both views 
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    // select div where emails are going to be displayed      
    const showEmail = document.querySelector("#show-emails");

    // Show the div if hidden   
    showEmail.style.display = "block";  
    showEmail.innerHTML = "<h3>Emails</h3>"

    // create new div where all info about selected email goes to 
    const emailDiv = document.createElement("div"); 

    // add a class 
    emailDiv.className = "email"; 

    // create two arrays in order to use a loop for displaying all infos about email 
    const arr = ["From: ", "To: ", "Subject: ", "Timestamp: ", "Body: "];        
    const email_info = [sender, recipients, subject, timestamp, body];

    // for loop to append email info 
    for (let i = 0; i < arguments.length; i++)
    {
        // send a PUT request to change value for read to true meaning this email is now read 
        if (i === arguments.length - 1)
        {            
            fetch(`/emails/${email_id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    read: true
                })
            })
        }
        // append email infos 
        else
        {
            const p = document.createElement("p");
            p.innerHTML = arr[i]  + email_info[i]; 
            emailDiv.appendChild(p); 
        }
    } 
    // sent emails cannot be replied   
    if (document.getElementById("from").value !== sender)
    {
        const button = document.createElement("button");  

        button.innerHTML = "Reply"; 
        emailDiv.appendChild(button); 

        button.onclick = () => {
            compose_email(true, sender, subject, timestamp, body );             
        }
    }
    // show email 
    showEmail.appendChild(emailDiv); 
}  