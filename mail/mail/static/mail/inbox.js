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
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#message-view').style.display = 'none';
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
        <span class="col-2 font-weight-bold pl-2">${email.sender}</span>
        <span class="col">${email.subject}</span>
        <span class="col-3 pr-0">${email.timestamp}</span>
        </div>
        `;
      div.addEventListener("click", () => view_email(email.id, mailbox !== "sent"));
      document.getElementById("emails-view").append(div);
    });
  })
  .catch(error => {
    console.log("Internal error: ", error);
  });
}

function view_email(id, show_inbox_buttons) {
  // Show the message and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Get message and mark as read
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    // Create reply and archive buttons for emails in inbox
    let inbox_buttons;
    if (show_inbox_buttons) {
      inbox_buttons = `
        <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
        <button class="btn btn-sm btn-outline-primary" id="toggle-archive">
        ${email.archived ? "Unarchive" : "Archive"}
        </button>
        `;
    } else {
      inbox_buttons = "";
    }

    // Create a div for header
    const hdr_div = document.createElement("div");
    hdr_div.className = "";
    hdr_div.innerHTML = `
      <div><strong>From: </strong>${email.sender}</div>
      <div><strong>To: </strong>${email.recipients.join(", ")}</div>
      <div><strong>Subject: </strong>${email.subject}</div>
      <div><strong>Timestamp: </strong>${email.timestamp}</div>
      ${inbox_buttons}
      <hr>
      `;
    document.getElementById("message-view").replaceChildren(hdr_div);

    // Attach event listeners for inbox buttons
    if (show_inbox_buttons) {
      document.getElementById("toggle-archive").addEventListener("click", () => {
        update_email_attr(id, "archived", !email.archived);
        load_mailbox("inbox");
      });
    }

    // Create a div for body
    const body_div = document.createElement("div");
    body_div.innerHTML = "<div>" + email.body.replace(/\r?\n/g, "</div><div>") + "</div>";
    document.getElementById("message-view").append(body_div);

    // Mark as read
    if (!email.read) {
      update_email_attr(id, "read", true)
    }
  })
  .catch(error => {
    console.log("Internal error: ", error);
  });
}

function update_email_attr(id, attr, value) {
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        [attr]: value,
    })
  })
  .then(response => { 
      if (!response.ok) {
        console.log("Error in update_email_attr request");
    }
  })
  .catch(error => {
    console.log("Internal error: ", error);
  });
}