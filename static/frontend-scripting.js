const form = document.getElementById("uploadForm");
const waitingParagraph = document.getElementById("waiting");
const fileControl = document.getElementById("file");
const linksParagraph = document.getElementById("linksParagraph");
const linksList = document.getElementById("linksList");

async function uploadFile() {
    const inputFile = fileControl.files[0];
    
    if (!inputFile) {
        alert("Please select a file to upload.");
        return;
    }
    
    const name = inputFile.name;

    const formData = new FormData(form);

    const response = await fetch("start-render", {
        method: "POST",
        body: formData
    });
    if (!response.ok) {
        alert("Error! Please try again.");
        return;
    }
    const result = await response.json();
    const task_name = result.task_name

    fileControl.value = null;
    form.style.display = "none";
    waitingParagraph.style.display = "";

    const interval = 1000; // Poll once a second
    const checkUrl = `check-render/${task_name}`;
    const getUrl = `get-render/${task_name}`;

    async function poll() {
        const response = await fetch(checkUrl, {method: "GET"});
        if (!response.ok) {
            alert("Error!  Please try again.");
            return;
        }
        const result = await response.json();

        if (!result.done) {
            setTimeout(poll, interval);
            return;
        }

        window.open(getUrl, "_blank");

        form.style.display = "";
        waitingParagraph.style.display = "none";

        linksParagraph.style.display = "";
        linksList.innerHTML = `<li><a href="${getUrl}" target="_blank">${name}</a></li>` + linksList.innerHTML;
    }

    poll();

}
