function editPost(editURL) {
    const editLink = event.target;
    const csrftoken = getCookie('csrftoken');
    editLink.style.display = "none";
    const postTextDiv = editLink.parentElement.parentElement.querySelector(".post-text");
    const postText = postTextDiv.innerHTML.trim().replaceAll("<br>", "\n");
    postTextDiv.innerHTML = `
        <form>
        <div class="form-group">
            <textarea id="edit-text" class="form-control" maxlength="280" rows="6">${postText}</textarea>
        </div>
        <input type="submit" value="Save" class="btn btn-primary">
        </form>
    `;
    postTextDiv.addEventListener("submit", function updatePostText() {
        postTextDiv.removeEventListener("submit", updatePostText);
        const newPostText = postTextDiv.querySelector("#edit-text").value;
        postTextDiv.innerHTML = newPostText.replaceAll("\n", "<br>");
        editLink.style.display = "inline";
        const formData = new FormData();
        formData.append('text', newPostText);
        fetch(editURL, {
            method: "POST",
            headers: {"X-CSRFToken": csrftoken},
            mode: "same-origin",
            body: formData, 
        })
        .then(response => {
            if (!response.ok) {
                console.log("Error saving updated post")
            }
        })
        .catch(error => {
            console.log("Internal error: ", error)
        });
        event.preventDefault();
    });
    event.preventDefault();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
