document.addEventListener("DOMContentLoaded", function() {
    updateAppointments();
    checkMessages();
    setInterval(() => {
        updateAppointments();
        checkMessages();
    }, 600000);
})

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

function DoctorInput(event) {
    //check for select value and add the doctor
    el = event.target;
    value = el.value;
    var container = document.getElementById("doctor");
    var description = container.children[0].children[0];
    var skill = document.getElementById("skills");
    if (value == "Doctor") {
        fetch("/skills", {
                method: "GET"
            })
            .then(response => response.json().then(skills => {
                if (response.status == 201) {
                    //add the new inputs
                    container.style.display = "block";
                    description.required = true;
                    skill.required = true;
                    for (let i = 0; i < skills.length; i++) {
                        const opt = document.createElement("option");
                        opt.value = skills[i].skill;
                        opt.innerText = skills[i].skill;
                        skill.append(opt)
                    }
                    // console.log(description.parentElement.nextElementSibling);
                }
            }))
            .catch(error => {
                console.log(error)
            })
    } else {
        container.style.display = "none";
        description.required = false;
        skill.required = false;
        for (let i = 0; i < skill.length; i++) {
            skill.children[i].remove()
        }
    }
}

function editDocProfile(id, first_name, last_name, profilepic) {
    var container = document.getElementById("doctors");
    fetch(`/doctor-profile/${id}`, {
            method: "GET",
        })
        .then(res => res.json().then(docprofille => {
            var doc = document.createElement("div");
            var imagecontainer = document.createElement("div");
            var textcontainer = document.createElement("div");
            var img = document.createElement("img");
            var name = document.createElement("h3");
            var descr = "";
            var skills = "";
            var btn = document.createElement("button");
            btn.innerHTML = "View Details";
            btn.className = "btn btn-primary view_details";
            img.src = `${profilepic}`;
            name.innerHTML = `${first_name} ${last_name}`;
            if (res.status == 201) {
                var descr = document.createElement("p");
                var skills = document.createElement("ul");
                descr.innerHTML = `${docprofille.descr}`;
                for (let i = 0; i < docprofille.skills.length; i++) {
                    const li = document.createElement("li");
                    li.innerHTML = `${docprofille.skills[i].skill}`;
                    skills.append(li);
                }
            }
            doc.className = "doctor-profile row";
            imagecontainer.className = "image col-sm-12 col-md-5 col-lg-4";
            textcontainer.className = "text col-sm-12 col-md-7 col-lg-8";
            textcontainer.append(name, descr, skills, btn);
            imagecontainer.append(img);
            doc.append(imagecontainer, textcontainer);
            // doc.setAttribute("onClick", `showDocDetails(${doctor[i].username})`);
            btn.onclick = () => {
                showDocDetails(id, first_name, last_name, profilepic);
            }
            container.append(doc)
        }))
        .catch(error => {
            console.log(error);
        })
}

function DocProfile(page_num, max_num) {
    if (page_num <= max_num) {
        fetch(`/get-doctors/${page_num}`, {
                method: "GET",
            })
            .then(response => response.json().then(doctor => {
                if (response.status == 201) {
                    //infinite scroll
                    for (let i = 0; i < doctor.length; i++) {
                        editDocProfile(doctor[i].id, doctor[i].first_name, doctor[i].last_name, doctor[i].profilepic)

                    }
                    window.onscroll = () => {
                        //check if next page exists
                        if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
                            var page = page_num + 1;
                            if (page <= max_num) {
                                DocProfile(page, max_num);
                            }
                        }
                    }
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }
}

function showDocDetails(id, first_name, last_name, profilepic) {
    var container = document.querySelector(".doctor-single");
    if (container.style.opacity == 0) {
        fetch(`/doctor-profile/${id}`, {
                method: "GET",
            })
            .then(response => response.json().then(doc => {
                if (response.status == 201) {
                    var imagecontainer = document.createElement("div");
                    var textcontainer = document.createElement("div");
                    var img = document.createElement("img");
                    var name = document.createElement("h3");
                    var btn = document.createElement("button");
                    btn.innerHTML = `
                    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 21L11 11L21 21M21 1L10.9981 11L1 1" stroke="black" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>                    
                    `;
                    btn.className = "cancel-single";
                    btn.onclick = () => {
                        showDocDetails(id, first_name, last_name, profilepic);
                    }
                    img.src = `${profilepic}`;
                    name.innerHTML = `${first_name} ${last_name}`;
                    var descr = document.createElement("p");
                    descr.innerHTML = `${doc.descr}`;
                    var skills = document.createElement("ul");
                    skills.className = "doctor-skills";
                    if (doc.skills.length > 0) {
                        for (let i = 0; i < doc.skills.length; i++) {
                            const li = document.createElement("li");
                            li.innerHTML = `${doc.skills[i].skill}`;
                            skills.append(li);
                        }
                    } else {
                        skills.innerHTML = "No skills";
                    }
                    var headeravail = document.createElement("h3");
                    headeravail.innerHTML = "Appointments available to be added";
                    var availables = document.createElement("ul");
                    availables.className = "doc-available";
                    var headerpatient = document.createElement("h3");
                    headerpatient.innerHTML = "Appointments you have made with the doctor";
                    var patientappointment = document.createElement("ul");
                    patientappointment.className = "patient-appointments";
                    if (doc.available.length > 0) {
                        for (let i = 0; i < doc.available.length; i++) {
                            const li = document.createElement("li");
                            li.innerHTML = `${doc.available[i].startdate} to ${doc.available[i].enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.available[i].id})" data-remove="Remove appointment" data-add="Add appointment">Add appointment</button>`;
                            availables.append(li);
                        }
                    } else {
                        availables.innerHTML = "Doctor hasn't created any appointment yet";
                    }
                    var mainuser = document.querySelector("#welcome").dataset.name;
                    if (doc.appointments.length > 0) {
                        //check if the patient is the user to get his appointment
                        for (let i = 0; i < doc.appointments.length; i++) {
                            if (doc.appointments[i].patient.username == mainuser) {
                                const li = document.createElement("li");
                                li.innerHTML = `${doc.appointments[i].appointment.startdate} to ${doc.appointments[i].appointment.enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.appointments[i].appointment.id})" data-remove="Remove appointment" data-add="Add appointment">Remove appointment</button>`;
                                patientappointment.append(li);
                            }
                        }
                    } else {
                        patientappointment.innerHTML = "You have not made any appointments with this doctor yet";
                    }
                    imagecontainer.className = "image";
                    textcontainer.className = "text";
                    textcontainer.append(name, descr, skills, headeravail, availables, headerpatient, patientappointment, btn);
                    imagecontainer.append(img);
                    var maincontainer = document.createElement("div");
                    maincontainer.className = "doctor-cover"
                    maincontainer.append(imagecontainer, textcontainer);
                    container.append(maincontainer);
                    container.style.opacity = 1;
                    container.style.pointerEvents = "all";
                } else {
                    alert("Something went wrong");
                }
            }))
    } else if (container.style.opacity == 1) {
        container.style.opacity = 0;
        container.style.pointerEvents = "none";
        container.innerHTML = "";
    }
}

function showSearchOptions(event) {
    //
    var el = event.target;
    var parent = el.parentElement.parentElement;
    var container = document.querySelector(".searchoptions");
    container.style.display = "block";
    for (let i = 0; i < container.children.length; i++) {
        container.children[i].onclick = (event) => {
            var el = event.target;
            parent.dataset.search = el.dataset.search;
            container.style.display = "none";
        }
    }
}

function submitSearch(event) {
    event.preventDefault()
    var el = event.target;
    var search = document.querySelector("[name='search']").value;
    var csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
    var container = document.querySelector(".searchoptions");
    container.style.display = "none";
    if (search != "") {
        fetch(`/search-doctors/${el.dataset.search}/${search}`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf,
                }
            })
            .then(response => response.json().then(res => {
                document.querySelector("[name='search']").value = "";
                var container = document.getElementById("doctors");
                container.innerHTML = "";
                if (response.status == 201) {
                    //run on a loop on th results and get the doctor profile
                    if (res.message) {
                        container.innerHTML = `<p class="not-found">${res.message}</p>`;
                    } else {
                        for (let i = 0; i < res.length; i++) {
                            editDocProfile(res[i].id, res[i].first_name, res[i].last_name, res[i].profilepic);
                        }
                    }
                }
            }))
            .catch(error => {
                console.log(error);
            })
    }
}

function showAdd(event) {
    var form = event.target.nextElementSibling;
    if (form.style.display == "none") {
        var formerror = document.getElementById("formerror");
        formerror.innerHTML = "";
        form.style.display = "block";
        event.target.innerHTML = event.target.dataset.change;
    } else {
        form.style.display = "none";
        event.target.innerHTML = event.target.dataset.changed;
    }
}

function addAvailability(event) {
    event.preventDefault()
    var csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
    var datetime = document.querySelector("[name='datetimes']").value;
    var error = document.querySelector("#formerror");
    var form = document.getElementById("availableform");
    var submit = document.querySelector("[name='submit']");
    submit.value = submit.dataset.loading;
    setTimeout(() => {
        fetch("/add-availability", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'X-CSRFToken': csrf,
                },
                body: JSON.stringify({
                    "datetimes": datetime,
                })
            })
            .then(response => response.json().then(res => {
                submit.value = submit.dataset.loaded;
                if (response.status == 201) {
                    var formerror = document.getElementById("formerror");
                    formerror.innerHTML = "";
                    var btn = document.getElementById("availbtn");
                    var container = document.querySelector(".available");
                    container.innerHTML = "";
                    var availability = res.available;
                    for (let i = 0; i < availability.length; i++) {
                        var tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td>${availability[i].startdate}</td>
                            <td>${availability[i].enddate}</td>
                            <td><button class="btn btn-primary" onclick="removeAvailabilty(event,${availability[i].id})">Remove availability</button></td>
                        `;
                        container.append(tr);
                    }
                    form.style.display = "none";
                    btn.innerHTML = btn.dataset.changed;
                    document.querySelector("[name='datetimes']").value = "";
                    checkMessages();
                } else {
                    //add the error
                    error.style.display = "block";
                    error.innerHTML = res.message;
                }
            }))
    }, 1500);
}

function removeAvailabilty(event, id) {
    var confirmdel = confirm("Do you really want to delete this availability?")
    if (confirmdel) {
        fetch(`/remove-availability/${id}`, {
                method: "PUT",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => response.json().then(res => {
                if (response.status == 201) {
                    var container = document.querySelector(".available");
                    container.innerHTML = "";
                    var availability = res.available;
                    for (let i = 0; i < availability.length; i++) {
                        var tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td>${availability[i].startdate}</td>
                            <td>${availability[i].enddate}</td>
                            <td><button class="btn btn-primary" onclick="removeAvailabilty(event,${availability[i].id})">Remove availability</button></td>
                        `;
                        container.append(tr);
                    }
                    checkMessages();
                } else {
                    alert(res.message)
                }
            }))
    }

}

function addAppointment(event, id) {
    //check whether to add or remove
    el = event.target;
    if (el.innerText == el.dataset.add) {
        //add appointment
        el.style.opacity = 0.7;
        el.innerText = "Adding..";
        setTimeout(() => {
            fetch(`/add-appointment/${id}`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFToken": getCookie('csrftoken'),
                    }
                })
                .then(response => response.json().then(doc => {
                    if (response.status == 201) {
                        //update the patient appointments and available appointment
                        var availables = document.querySelector(".doc-available");
                        var patientappointment = document.querySelector(".patient-appointments");
                        availables.innerHTML = "";
                        patientappointment.innerHTML = "";
                        if (doc.available.length > 0) {
                            for (let i = 0; i < doc.available.length; i++) {
                                const li = document.createElement("li");
                                li.innerHTML = `${doc.available[i].startdate} to ${doc.available[i].enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.available[i].id})" data-remove="Remove appointment" data-add="Add appointment">Add appointment</button>`;
                                availables.append(li);
                            }
                        } else {
                            availables.innerHTML = "Doctor hasn't created any appointment yet";
                        }
                        var mainuser = document.querySelector("#welcome").dataset.name;
                        if (doc.appointments.length > 0) {
                            //check if the patient is the user to get his appointment
                            for (let i = 0; i < doc.appointments.length; i++) {
                                if (doc.appointments[i].patient.username == mainuser) {
                                    const li = document.createElement("li");
                                    li.innerHTML = `${doc.appointments[i].appointment.startdate} to ${doc.appointments[i].appointment.enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.appointments[i].appointment.id})" data-remove="Remove appointment" data-add="Add appointment">Remove appointment</button>`;
                                    patientappointment.append(li);
                                }
                            }
                        } else {
                            patientappointment.innerHTML = "You have not made any appointments with this doctor yet";
                        }
                        el.style.opacity = 1;
                        checkMessages();
                    } else {
                        alert(doc.message);
                        el.innerText = el.dataset.add;
                        el.style.opacity = 1;
                    }
                }))
                .catch(error => {
                    console.log(error)
                })
        }, 1000);
    } else if (el.innerText == el.dataset.remove) {
        //remove appointment
        el.style.opacity = 0.7;
        el.innerText = "Removing..";
        setTimeout(() => {
            fetch(`/remove-appointment/${id}`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFToken": getCookie('csrftoken'),
                    }
                })
                .then(response => response.json().then(doc => {
                    if (response.status == 201) {
                        checkMessages();
                        //update the patient appointments and available appointment
                        var availables = document.querySelector(".doc-available");
                        var patientappointment = document.querySelector(".patient-appointments");
                        availables.innerHTML = "";
                        patientappointment.innerHTML = "";
                        if (doc.available.length > 0) {
                            for (let i = 0; i < doc.available.length; i++) {
                                const li = document.createElement("li");
                                li.innerHTML = `${doc.available[i].startdate} to ${doc.available[i].enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.available[i].id})" data-remove="Remove appointment" data-add="Add appointment">Add appointment</button>`;
                                availables.append(li);
                            }
                        } else {
                            availables.innerHTML = "Doctor hasn't created any appointment yet";
                        }
                        var mainuser = document.querySelector("#welcome").dataset.name;
                        if (doc.appointments.length > 0) {
                            //check if the patient is the user to get his appointment
                            for (let i = 0; i < doc.appointments.length; i++) {
                                if (doc.appointments[i].patient.username == mainuser) {
                                    const li = document.createElement("li");
                                    li.innerHTML = `${doc.appointments[i].appointment.startdate} to ${doc.appointments[i].appointment.enddate}<button class="btn btn-primary" onclick="addAppointment(event,${doc.appointments[i].appointment.id})" data-remove="Remove appointment" data-add="Add appointment">Remove appointment</button>`;
                                    patientappointment.append(li);
                                }
                            }
                        } else {
                            patientappointment.innerHTML = "You have not made any appointments with this doctor yet";
                        }
                        el.style.opacity = 1;
                    } else {
                        alert(doc.message);
                        el.innerText = el.dataset.remove;
                        el.style.opacity = 1;
                    }
                }))
                .catch(error => {
                    console.log(error)
                })
        }, 1000);
    }
}

function removeAppointment(event, id) {
    //check whether to add or remove
    el = event.target;
    if (el.innerText == el.dataset.remove) {
        //remove appointment
        el.style.opacity = 0.7;
        el.innerText = "Removing..";
        setTimeout(() => {
            fetch(`/remove-appointment/${id}`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFToken": getCookie('csrftoken'),
                    }
                })
                .then(response => response.json().then(doc => {
                    if (response.status == 201) {
                        //update the patient appointments and available appointment
                        el.parentElement.parentElement.remove()
                        checkMessages();
                    } else {
                        alert(doc.message);
                        el.innerText = el.dataset.remove;
                        el.style.opacity = 1;
                    }
                }))
                .catch(error => {
                    console.log(error)
                })
        }, 1000);
    }
}

function addDrug(id, pic, name, descr, price, container) {
    const drug = document.createElement("div");
    drug.className = "drug";
    drug.innerHTML = `<div class="row drug-top">
        <div class="drug-top-image">
            <img src="${pic}" alt="${name}"/>
        </div>
    </div>
    <div class="drug-bottom">
        <div class="col drug-top-text">
            <h3> ${name} </h3>
        </div>
        <p class="drug-descr"> ${descr} </p>
        <p class="drug-price">Price: $${price} a piece </p>
        <button class="btn btn-primary" data-viewed="Close details" data-view="View details" onclick="viewDrug(event,${id})")>View details</button>
    </div>
    `
    container.append(drug);
}

function getDrugs(page_num, max_num) {
    var container = document.querySelector(".drugs");
    if (page_num <= max_num) {
        fetch(`/get-drugs/${page_num}`, {
                method: "GET",
            })
            .then(response => response.json().then(drugs => {
                if (response.status == 201) {
                    container.innerHTML = "";
                    document.querySelector("[name='drug_search']").value = "";
                    for (let i = 0; i < drugs.length; i++) {
                        addDrug(drugs[i].id, drugs[i].drugpic, drugs[i].name, drugs[i].descr, drugs[i].price, container);
                    }
                    var pagination = document.querySelector("nav.pagination")
                    pagination.style.display = "block";
                    const prevbtn = document.querySelector(".previous");
                    const nextbtn = document.querySelector(".next");
                    var pagenext = page_num + 1;
                    var pageprev = page_num - 1;
                    //update prev and next buttons
                    if (page_num > 1) {
                        prevbtn.onclick = () => {
                            getDrugs(pageprev, max_num)
                        }
                    } else if (pagenext <= max_num) {
                        nextbtn.setAttribute("onclick", `getDrugs(${pagenext}, ${max_num})`);
                    }
                }
            }))
            .catch(error => {
                console.log(error);
            })
    }
}

function searchDrugs(event) {
    event.preventDefault()
    var search = document.querySelector("[name='drug_search']").value;
    var csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
    var container = document.querySelector(".drugs");
    if (search != "") {
        fetch(`/search-drugs`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrf,
                },
                body: JSON.stringify({
                    "term": search,
                })
            })
            .then(response => response.json().then(drugs => {
                if (response.status == 201) {
                    document.querySelector("[name='drug_search']").value = "";
                    container.innerHTML = "";
                    if (drugs.message) {
                        container.innerHTML = drugs.message
                    } else {
                        for (let i = 0; i < drugs.length; i++) {
                            addDrug(drugs[i].id, drugs[i].drugpic, drugs[i].name, drugs[i].descr, drugs[i].price, container);
                        }
                        var pagination = document.querySelector("nav.pagination")
                        pagination.style.display = "none";
                    }
                } else {
                    console.log(drugs.message)
                }
            }))
            .catch(error => {
                console.log(error);
            })
    }
}

function viewDrug(event, id) {
    el = event.target;
    var container = document.getElementById("drug-single");
    if (container.style.opacity == 0) {
        //show the drug details
        fetch(`/drug-details/${id}`, {
                method: "GET",
            })
            .then(response => response.json().then(drug => {
                container.innerHTML = "";
                if (response.status == 201) {
                    //check if the drug is the user's cart
                    fetch(`/drug-order/${drug.id}`, {
                            method: "GET",
                        })
                        .then(res => res.json().then(checker => {
                            container.innerHTML = `
                             <div class="drug-single-main">
                                <div class="image">
                                    <img src="${drug.drugpic}" alt="${drug.name}">
                                </div>
                                <div class="text">
                                    <h3>${drug.name}</h3>
                                    <p class="descr">${drug.descr}</p>
                                    <p class="prescr"><h4>Prescription</h4><br/><span>${drug.prescription}</span></p>
                                    <p class="price">Price: $${drug.price}</p>
                                    <p class="stock">We have ${drug.instock} packs in stock</p>
                                    <form enctype="multipart/form-data" target="stopperframe" id="checkout-form" method="POST" onsubmit="submitCheckout(event, ${drug.id})">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                                        <div class="form-group">
                                            <label for="order_pieces" class="form-label">Pieces you want to order</label>
                                            <input type="number" name="order_pieces" class="form-control" required/>
                                        </div>
                                        <input type="submit" class="btn btn-secondary checkout" value="Checkout">
                                    </form><br/>
                                </div>
                             </div>
                            `

                            if (res.status == 201) {
                                var rowbutton = document.createElement("div");
                                var cancelbtn = document.createElement("button");
                                cancelbtn.className = "cancel-single";
                                cancelbtn.innerHTML = `
                                <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M1 21L11 11L21 21M21 1L10.9981 11L1 1" stroke="black" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>  
                                `;
                                cancelbtn.onclick = () => {
                                    viewDrug(event, drug.id)
                                }
                                var cartbtn = document.createElement("button");
                                cartbtn.className = "btn btn-primary";
                                cartbtn.dataset.removed = "Remove from cart";
                                cartbtn.dataset.added = "Add to cart";
                                if (checker.message == true) {
                                    cartbtn.innerText = cartbtn.dataset.removed;
                                } else if (checker.message == false) {
                                    cartbtn.innerText = cartbtn.dataset.added;
                                }
                                cartbtn.setAttribute("onclick", `addCart(event, ${drug.id})`)
                                rowbutton.append(cartbtn)
                                container.children[0].children[1].append(rowbutton, cancelbtn);


                                container.style.opacity = 1;
                                container.style.pointerEvents = "all";
                            } else {
                                console.log(res.message)
                            }
                            // document.getElementById("checkout-form").onsubmit = () => {
                            //     submitCheckout(event, drug.id);
                            // }
                        }))
                } else {
                    container.innerHTML = drug.message;
                }
            }))
    } else if (container.style.opacity == 1) {
        //hide drug details
        container.style.opacity = 0;
        container.style.pointerEvents = "none";
    }
}

function addCart(event, id) {
    el = event.target;
    console.log(el);
    console.log(el.parentElement);
    console.log(el.nextElementSibling);
    if (el.innerText == el.dataset.added) {
        console.log("it clickced");
        //add to cart
        el.innerText = "Adding..."
        el.style.opacity = "0.7";
        setTimeout(() => {
            fetch(`/add-cart`, {
                    method: "PUT",
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        "pk": id,
                    })
                })
                .then(response => response.json().then(res => {
                    if (response.status == 201) {
                        el.innerText = el.dataset.removed;
                        el.style.opacity = "1";
                        checkMessages();
                    } else {
                        console.log(res.message);
                        el.innerText = el.dataset.added;
                        el.style.opacity = "1";
                    }
                }))
        }, 1000);
    } else if (el.innerText == el.dataset.removed) {
        //remove from cart
        el.innerText = "Removing..."
        el.style.opacity = "0.7";
        setTimeout(() => {
            fetch(`/remove-cart`, {
                    method: "PUT",
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        "pk": id,
                    })
                })
                .then(response => response.json().then(res => {
                    if (response.status == 201) {
                        el.innerText = el.dataset.added;
                        el.style.opacity = "1";
                        checkMessages();
                    } else {
                        console.log(res.message);
                        el.innerText = el.dataset.removed;
                        el.style.opacity = "1";
                    }
                }))
        }, 1000);
    }
}

function submitCheckout(event, id) {
    event.preventDefault();
    const el = event.target;
    var pieces = el.children[1].children[1].value;
    var csrf = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    fetch(`/checkout`, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrf,
            },
            body: JSON.stringify({
                "pieces": pieces,
                "pk": id,
            })
        })
        .then(response => response.json().then(res => {
            el.children[1].children[1].value = "";
            if (response.status == 201) {
                var parent = el.parentElement;
                checkMessages();
                if (parent.className == "drug-bottom") {
                    //for cart checkout
                    const amount = parent.children[1];
                    const price = parent.children[2];
                    amount.innerHTML = `Amount ordered: ${res.amount} piece(s)`;
                    price.innerHTML = `Total amount: $${res.price}`;
                } else {
                    const checkoutsuccess = document.getElementById("checkoutsuccess");
                    if (!checkoutsuccess) {
                        const checkoutsuccess = document.createElement("p");
                        checkoutsuccess.id = "checkoutsuccess"
                        el.append(checkoutsuccess)
                        el.insertBefore(checkoutsuccess, el.children[0])
                        checkoutsuccess.innerHTML = res.message;
                    } else if (checkoutsuccess) {
                        checkoutsuccess.innerHTML = res.message;
                    }
                }
            } else {
                console.log(res.message);
            }
        }))
        .catch(error => {
            console.log(error)
        })
}

function viewMessage(event, id) {
    el = event.target;
    var container = document.querySelector(".message-single");
    if (container.style.opacity == 0) {
        fetch(`/message-details`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    "pk": id,
                })
            })
            .then(response => response.json().then(message => {
                container.innerHTML = "";
                if (response.status == 201) {
                    const parent = el.parentElement.parentElement;
                    parent.className = "message read row";
                    const header = document.createElement("h3");
                    const body = document.createElement("div");
                    body.className = "inner-message"
                    const timestamp = document.createElement("p");
                    header.innerHTML = message.subject;
                    body.innerHTML = message.body;
                    const cover = document.createElement("div");
                    cover.className = "message-cover";
                    var cancelbtn = document.createElement("button");
                    cancelbtn.className = "cancel-single";
                    cancelbtn.innerHTML = `
                    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 21L11 11L21 21M21 1L10.9981 11L1 1" stroke="black" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>  
                    `;
                    cancelbtn.onclick = () => {
                        viewMessage(event, message.id)
                    }
                    timestamp.innerHTML = message.timestamp;
                    cover.append(header, body, timestamp);
                    container.append(cover, cancelbtn);
                    container.classList.add("active-message");
                    container.style.opacity = 1;
                    container.style.pointerEvents = "all";
                    setTimeout(() => {
                        checkMessages();
                    }, 1000);
                } else {
                    console.log(message.message)
                }
            }))
    } else if (container.style.opacity == 1) {
        container.style.opacity = 0;
        container.style.pointerEvents = "none";
        container.innerHTML = "";
        container.classList.remove("active-message");
    }
}

function updateAppointments() {
    fetch(`/update-appointments`, {
            method: "GET",
        })
        .then(response => response.json().then(res => {
            if (response.status == 201) {
                // console.log(res.message)
            } else {
                console.log(res.message)
            }
        }))
        .catch(error => {
            console.log(error)
        })
}

function addComplete(event, id) {
    el = event.target;
    var container = document.querySelector(".inner-message");
    if (el.innerText == "Attended") {
        //add completion
        fetch(`/add_complete/${id}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    "command": "add",
                })
            })
            .then(response => response.json().then(res => {
                container.innerHTML = "";
                if (response.status == 201) {
                    container.innerHTML = res.message;
                    setTimeout(() => {
                        checkMessages()
                    }, 1000);
                } else {
                    console.log(res.message);
                }
            }))
            .catch(error => {
                console.log(error)
            })
    } else if (el.innerText == "Not Attended") {
        //remove completion
        fetch(`/add_complete/${id}`, {
                method: "PUT",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    "command": "remove",
                })
            })
            .then(response => response.json().then(res => {
                container.innerHTML = "";
                if (response.status == 201) {
                    container.innerHTML = res.message;
                    setTimeout(() => {
                        checkMessages()
                    }, 1000);
                } else {
                    console.log(res.message);
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }
}

function checkMessages() {
    var message = document.querySelector("#messages-check");
    if (message) {
        fetch(`/new-messages`, {
                method: "GET",
            })
            .then(response => response.json().then(status => {
                if (response.status == 201) {
                    if (status.message) {
                        //means now new messages
                        message.innerHTML = "Message(0)";
                    } else if (status.status) {
                        //means there are unread messages
                        message.innerHTML = `Messages(${status.status})`;
                    }
                }
            }))
            .catch(error => {
                console.log(error)
            })
    }
}

function getMessages(page_num, max_page) {
    var parent = document.querySelector(".messages_container");
    if (page_num <= max_page) {
        fetch(`/get-messages/${page_num}`, {
                method: "GET",
            })
            .then(response => response.json().then(message => {
                if (response.status == 201) {
                    parent.innerHTML = "";
                    for (let i = 0; i < message.length; i++) {
                        var container = document.createElement("div")
                        container.className = "message row";
                        if (message[i].read == true) {
                            container.classList.add("read");
                        } else if (message[i].read == false) {
                            container.classList.add("unread")
                        }
                        container.innerHTML = `
                        <div class="text col-sm-12 col-md-9 col-lg-9">
                            <h4>${message[i].subject}</h4>
                            <p>${message[i].timestamp}</p>
                        </div>
                        <div class="action col-sm-12 col-md-3 col-lg-3">
                            <button class="btn btn-primary" onclick="viewMessage(event,${message[i].id})">View details</button>
                        </div>
                    `
                        parent.append(container);
                    }

                    //update the prev and next buttons
                    const prevbtn = document.querySelector(".previous");
                    const nextbtn = document.querySelector(".next");
                    var pagenext = page_num + 1;
                    var pageprev = page_num - 1;

                    //update prev and next buttons
                    if (page_num > 1) {
                        if (prevbtn) {
                            prevbtn.onclick = () => {
                                getMessages(pageprev, max_page)
                            }
                        }
                    } else if (pagenext <= max_page) {
                        if (nextbtn) {
                            nextbtn.setAttribute("onclick", `getMessages(${pagenext}, ${max_page})`);
                        }
                    }
                } else {
                    console.log(message);
                }
            }))
            .catch(error => {
                console.log(`Error: ${error}`)
            })
    }
}

function changePassword(event) {
    parent = event.target.parentElement;
    el = event.target;
    el.innerHTML = el.dataset.loading;
    var success = document.querySelector(".successmessage");
    if (!success) {
        var success = document.createElement("p");
        success.className = "successmessage text-success";
        parent.append(success)
        parent.insertBefore(success, parent.children[0])
        setTimeout(() => {
            fetch(`/change-password`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFToken": getCookie('csrftoken'),
                    }
                })
                .then(response => response.json().then(res => {
                    el.innerHTML = el.dataset.loaded;
                    if (response.status == 201) {
                        var success = document.querySelector(".successmessage");
                        success.innerHTML = res.message;
                    } else {
                        console.log(res.message)
                    }
                }))
        }, 1000);
    } else {
        var question = confirm("You have requested earlier for a password verification,do you want us to resend");
        if (question) {
            success.remove();
            changePassword(event);
        } else {
            el.innerHTML = el.dataset.loaded;
        }
    }
}

function getCart(page_num, max_page) {
    var parent = document.querySelector(".drugs");
    if (page_num <= max_page) {
        fetch(`/cart-drugs/${page_num}`, {
                method: "GET",
            })
            .then(response => response.json().then(cart => {
                if (response.status == 201) {
                    parent.innerHTML = "";
                    for (let i = 0; i < cart.length; i++) {
                        var container = document.createElement("div")
                        container.className = "drug";
                        container.innerHTML = `
                        <div class="row drug-top">
                            <div class="drug-top-image">
                                <img src="${cart[i].drug.drugpic}" alt="${cart[i].drug.name}"/>
                            </div>
                        </div>
                        <div class="drug-bottom">
                            <div class="drug-top-text">
                                <h3> ${cart[i].drug.name} </h3>
                            </div>
                            <p class="drug-descr"> ${cart[i].drug.descr} </p>
                            <p class="drug-price">Amount ordered: ${cart[i].amount} piece(s) </p>
                            <p class="drug-price">Total amount: $${cart[i].price} </p>
                            <p class="drug-price">Price per piece: $${cart[i].drug.price} </p>
                            <form enctype="multipart/form-data" target="stopperframe" id="checkout-form" method="POST" onsubmit="submitCheckout(event, ${cart[i].drug.id})">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                                <div class="form-group">
                                    <label for="order_pieces" class="form-label">How many pieces</label>
                                    <input type="number" name="order_pieces" class="form-control" required/>
                                </div>
                                <input type="submit" class="btn btn-primary" value="Change amount ordered">
                            </form>
                            <button class="btn btn-primary" data-removed="Remove from cart" data-added="Add to cart" onclick="addCart(event, ${cart[i].drug.id})">Remove from cart</button>
                        </div>
                        `
                        parent.append(container);
                    }

                    //update the prev and next buttons
                    const prevbtn = document.querySelector(".previous");
                    const nextbtn = document.querySelector(".next");
                    var pagenext = page_num + 1;
                    var pageprev = page_num - 1;

                    //update prev and next buttons
                    if (page_num > 1) {
                        if (prevbtn) {
                            prevbtn.onclick = () => {
                                getCart(pageprev, max_page)
                            }
                        }
                    } else if (pagenext <= max_page) {
                        if (nextbtn) {
                            nextbtn.setAttribute("onclick", `getCart(${pagenext}, ${max_page})`);
                        }
                    }
                } else {
                    console.log(message);
                }
            }))
            .catch(error => {
                console.log(`Error: ${error}`)
            })
    }
}

function getPatientAppointment(page_num, max_page) {
    var parent = document.querySelector("#patients");
    if (page_num <= max_page) {
        fetch(`/patient-appointments/${page_num}`, {
                method: "GET",
            })
            .then(response => response.json().then(appoint => {
                if (response.status == 201) {
                    parent.innerHTML = "";
                    for (let i = 0; i < appoint.length; i++) {
                        var container = document.createElement("tr");
                        container.innerHTML = `
                            <td><img src="${appoint[i].patient.profilepic}" alt="${appoint[i].patient.first_name}"/><span>${appoint[i].patient.first_name} ${appoint[i].patient.last_name}</span></td>
                            <td>${appoint[i].appointment.startdate}</td>
                            <td>${appoint[i].appointment.enddate}</td>
                            <td><button class="btn btn-warning text-white">Ongoing</button></td>
                        `
                        parent.append(container);
                    }

                    //update the prev and next buttons
                    const prevbtn = document.querySelector(".previous");
                    const nextbtn = document.querySelector(".next");
                    var pagenext = page_num + 1;
                    var pageprev = page_num - 1;

                    //update prev and next buttons
                    if (page_num > 1) {
                        if (prevbtn) {
                            prevbtn.onclick = () => {
                                getPatientAppointment(pageprev, max_page)
                            }
                        }
                    } else if (pagenext <= max_page) {
                        if (nextbtn) {
                            nextbtn.setAttribute("onclick", `getPatientAppointment(${pagenext}, ${max_page})`);
                        }
                    }
                } else {
                    console.log(message);
                }
            }))
            .catch(error => {
                console.log(`Error: ${error}`)
            })
    }
}