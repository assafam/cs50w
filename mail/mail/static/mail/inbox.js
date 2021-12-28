document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Compose email onsubmit
  document.getElementById("compose-form").addEventListener("submit", () => {
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.getElementById("compose-recipients").value,
          subject: document.getElementById("compose-subject").value,
          body: document.getElementById("compose-body").value,
      })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
          alert("Error: " + result.error)
        } else {
          load_mailbox("sent");
        }
    })
    .catch(error => {
      console.log("Internal error: ", error);
    });
    event.preventDefault();
  });
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get mails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const div = document.createElement("div");
      div.className = "container-fluid message";
      if (email.read) {
        div.className += " message-read";
      }
      div.innerHTML = `
        <div class="row">
        <span class="col-2 font-weight-bold pl-1">${email.sender}</span>
        <span class="col">${email.subject}</span>
        <span class="col-2 pr-0">${email.timestamp}</span>
        </div>
        `;
      div.addEventListener("click", view_email(email.id));
      document.getElementById("emails-view").append(div);
    });
  })
  .catch(error => {
    console.log("Internal error: ", error);
  });
}

function view_email(id) {
  console.log(id);
}