```javascript
/* =====================================================
   ONLINE COLLEGE ADMISSION
   JavaScript File
===================================================== */


/* =====================================================
   ADMISSION FORM
===================================================== */

const admissionForm = document.getElementById("admissionForm");


admissionForm.addEventListener("submit", function (event) {

    // Stop the form from submitting for now
    event.preventDefault();


    /* -------------------------------------------------
       GET FORM VALUES
    ------------------------------------------------- */

    const studentName =
        document.getElementById("studentName").value.trim();

    const mobile =
        document.getElementById("mobile").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const tenth =
        document.getElementById("tenth").value;

    const twelfth =
        document.getElementById("twelfth").value;

    const course =
        document.getElementById("course").value;

    const declaration =
        document.getElementById("declaration").checked;


    /* -------------------------------------------------
       CHECK STUDENT NAME
    ------------------------------------------------- */

    if (studentName.length < 3) {

        alert("Please enter a valid student name.");

        document.getElementById("studentName").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK MOBILE NUMBER
    ------------------------------------------------- */

    const mobilePattern = /^[6-9]\d{9}$/;


    if (!mobilePattern.test(mobile)) {

        alert(
            "Please enter a valid 10-digit Indian mobile number."
        );

        document.getElementById("mobile").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK EMAIL
    ------------------------------------------------- */

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    if (!emailPattern.test(email)) {

        alert("Please enter a valid email address.");

        document.getElementById("email").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK 10TH MARK
    ------------------------------------------------- */

    if (tenth < 0 || tenth > 100) {

        alert(
            "10th percentage must be between 0 and 100."
        );

        document.getElementById("tenth").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK 12TH MARK
    ------------------------------------------------- */

    if (twelfth < 0 || twelfth > 100) {

        alert(
            "12th percentage must be between 0 and 100."
        );

        document.getElementById("twelfth").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK COURSE
    ------------------------------------------------- */

    if (course === "") {

        alert("Please select a course.");

        document.getElementById("course").focus();

        return;
    }


    /* -------------------------------------------------
       CHECK DECLARATION
    ------------------------------------------------- */

    if (!declaration) {

        alert(
            "Please accept the declaration before submitting."
        );

        return;
    }


    /* -------------------------------------------------
       SUCCESS MESSAGE
    ------------------------------------------------- */

    alert(
        "Your admission form has been validated successfully!"
    );


    /*
       IMPORTANT:

       For now, the form is not being saved
       to a database.

       In the next step, we will connect this
       form to Python Flask and a database.
    */


});
```
