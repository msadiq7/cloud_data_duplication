// -----------------------------------
// LOAD RECORDS
// -----------------------------------

async function loadRecords() {

    try {

        const response = await fetch("/api/records");

        const records = await response.json();

        const table =
            document.getElementById("recordsTable");

        table.innerHTML = "";

        if (records.length === 0) {

            table.innerHTML = `
                <tr>
                    <td colspan="6"
                        style="text-align:center;padding:30px;color:#9ca3af;">
                        No records found.
                    </td>
                </tr>
            `;

            return;
        }


        records.forEach(record => {

            const row = document.createElement("tr");

            row.innerHTML = `

                <td>${record.id}</td>

                <td>
                    <strong>${escapeHTML(record.name)}</strong>
                </td>

                <td>${escapeHTML(record.email)}</td>

                <td>${escapeHTML(record.phone)}</td>

                <td>${record.created_at}</td>

                <td>

                    <button
                        class="delete-button"
                        onclick="deleteRecord(${record.id})">

                        Delete

                    </button>

                </td>
            `;

            table.appendChild(row);

        });

    } catch (error) {

        console.error(error);

    }
}


// -----------------------------------
// ADD RECORD
// -----------------------------------

document
    .getElementById("recordForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();


        const name =
            document.getElementById("name").value;

        const email =
            document.getElementById("email").value;

        const phone =
            document.getElementById("phone").value;


        const message =
            document.getElementById("message");


        message.className = "message";

        message.textContent = "Checking record...";


        try {

            const response = await fetch(
                "/api/records",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone
                    })
                }
            );


            const result =
                await response.json();


            if (result.success) {

                message.className =
                    "message success";

                message.textContent =
                    "✓ " + result.message;


                document
                    .getElementById("recordForm")
                    .reset();


                loadRecords();

                loadStats();

            }

            else {

                message.className =
                    "message error";


                if (result.errors) {

                    message.innerHTML =
                        "✗ " +
                        result.errors.join("<br>✗ ");

                }

                else {

                    message.textContent =
                        "✗ " + result.message;

                }

            }

        }

        catch (error) {

            message.className =
                "message error";

            message.textContent =
                "Something went wrong.";

            console.error(error);

        }

    });


// -----------------------------------
// DELETE RECORD
// -----------------------------------

async function deleteRecord(id) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this record?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/records/${id}`,
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (result.success) {

            loadRecords();

            loadStats();

        }

        else {

            alert(result.message);

        }

    }

    catch (error) {

        console.error(error);

        alert("Unable to delete record.");

    }
}


// -----------------------------------
// LOAD STATISTICS
// -----------------------------------

async function loadStats() {

    try {

        const response =
            await fetch("/api/stats");

        const data =
            await response.json();


        document
            .getElementById("totalRecords")
            .textContent = data.total;


        document
            .getElementById("verifiedRecords")
            .textContent = data.total;

    }

    catch (error) {

        console.error(error);

    }
}


// -----------------------------------
// CSV UPLOAD
// -----------------------------------

async function uploadCSV() {

    const fileInput =
        document.getElementById("csvFile");

    const message =
        document.getElementById("uploadMessage");


    if (!fileInput.files.length) {

        message.className =
            "message error";

        message.textContent =
            "✗ Please select a CSV file.";

        return;
    }


    const file =
        fileInput.files[0];


    const formData =
        new FormData();

    formData.append("file", file);


    message.className =
        "message";

    message.textContent =
        "Processing CSV...";


    try {

        const response =
            await fetch(
                "/api/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        const result =
            await response.json();


        if (result.success) {

            message.className =
                "message success";


            message.innerHTML = `
                ✓ CSV processed successfully.<br>
                New records: ${result.inserted}<br>
                Duplicates skipped: ${result.duplicates}<br>
                Invalid records: ${result.invalid}
            `;


            fileInput.value = "";


            loadRecords();

            loadStats();

        }

        else {

            message.className =
                "message error";

            message.textContent =
                "✗ " + result.message;

        }

    }

    catch (error) {

        console.error(error);

        message.className =
            "message error";

        message.textContent =
            "Something went wrong while uploading.";

    }
}


// -----------------------------------
// SECURITY
// -----------------------------------

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// -----------------------------------
// INITIAL LOAD
// -----------------------------------

document.addEventListener(
    "DOMContentLoaded",
    function() {

        loadRecords();

        loadStats();

    }
);