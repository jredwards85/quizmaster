// Remove autocomplete from all input fields
document.addEventListener('DOMContentLoaded', function () {
    // Add autocomplete="off" to all input fields
    let inputFields = document.querySelectorAll('input');
    inputFields.forEach(function (input) {
        input.setAttribute('autocomplete', 'off');
    });
});

// Hide messages after fadeout
document.addEventListener('DOMContentLoaded', function () {
    // Get the fade-out div
    let fadeDiv = document.getElementById('fadeDiv');

    if (fadeDiv) {
        // Add an event listener to start hiding the div when the animation ends
        fadeDiv.addEventListener('animationend', function () {
            fadeDiv.classList.add('hide-element'); // Add the 'hidden' class to apply display: none
        });
    }
  
    
  });

// Toggle search bar (in top menu for PC view only)
document.addEventListener('click', function (event) {
    let searchBar = document.getElementById('main-layout-top-menu-search');
    let toggleButton = document.getElementById('menu-bar-pc-search-icon');
    
    // Show search / hide button
    if (toggleButton.contains(event.target)) {
        searchBar.style.display = 'block';
        toggleButton.style.display = 'none';
    } else if (!searchBar.contains(event.target) && !toggleButton.contains(event.target)) {
        searchBar.style.display = 'none';
        toggleButton.style.display = 'block';
    }
});

// Toggle drop down menu (in top menu for PC view only)
document.addEventListener('click', function (event) {
    let menuBlock = document.getElementById('main-layout-top-menu-right-dropdown');
    let toggleButton = document.getElementById('main-layout-top-menu-right-svg');
    
    // Show search / hide button
    if (toggleButton.contains(event.target)) {
        if (menuBlock.style.display === 'none' || menuBlock.style.display === '') {
            menuBlock.style.display = 'block';
        } else {
            menuBlock.style.display = 'none';
        }
    } else if (!menuBlock.contains(event.target) && !toggleButton.contains(event.target)) {
        menuBlock.style.display = 'none'; 
    }
});

// Show mobile menu (in top menu for Mobile view only)
document.addEventListener('click', function (event) {
    let menuOverlay = document.getElementById('main-mobile-menu');
    let toggleButton = document.getElementById('menu-icon-mob');
    let body = document.body;

    if (toggleButton.contains(event.target)) {
        menuOverlay.style.display = 'block';
        body.style.overflow = 'hidden';
    } 
});

// Hide mobile menu (in menu overlay for Mobile view only)
document.addEventListener('click', function (event) {
    let menuOverlay = document.getElementById('main-mobile-menu');
    let toggleButton = document.getElementById('main-mobile-menu-x');
    let body = document.body;

    if (toggleButton.contains(event.target)) {
        menuOverlay.style.display = 'none';
        body.style.overflow = 'auto';
    }
});

// Show the named div
function toggleField(divID) {
    let show = document.getElementById(divID);

    if (show.style.display === 'none') {
        show.style.display = 'block';
    } else {
        show.style.display = 'none';
    }    
}

// Show the profile and edit window
function showFieldProfileEdit(divID) {
    let overlay = document.getElementById('profile-team-member-edit-overlay');
    let show = document.getElementById(divID);

    show.style.display = 'block';
    overlay.style.display = 'flex';

}

// Hide the profile and edit window
function hideFieldProfileEdit() {
    let overlay = document.getElementById('profile-team-member-edit-overlay');
    let hide = document.querySelectorAll('.profile-team-member-edit');

    hide.forEach(function(div) {
        div.style.display = 'none';
    })

    overlay.style.display = 'none';
}

// Profile avatar preview
function previewImage(divID) {
    let input = document.getElementById(`imageInput${divID}`);
    let preview = document.getElementById(`imagePreview${divID}`);
    let saveImageButton = document.getElementById(`saveImageButton${divID}`);
    
    console.log(divID)
    // Clear previous preview
    preview.innerHTML = '';

    if (input.files && input.files[0]) {
        // Display the "Save image" button
        saveImageButton.style.display = 'block';

        let reader = new FileReader();

        reader.onload = function (e) {
            // Create an image element for preview
            let img = document.createElement('img');
            img.src = e.target.result;

            // Apply properties to the image
            img.style.width = '100px';
            img.style.height = '100px';
            img.style.borderRadius = '50%';
            img.style.overflow = 'hidden';
            img.style.border = '0';
            img.style.padding = '4px';
            img.style.objectFit = 'cover';

            // Append the image to the preview div
            preview.appendChild(img);
        };

        reader.readAsDataURL(input.files[0]);


    } else {
        saveImageButton.style.display = 'none';
    }
}

// Confirm delele popup
function confirmDelete(event, id) {
    if (id === 'del_acc') {
        let confirmed = confirm("Are you sure you want to delete your account?");
        if (!confirmed) {
            event.preventDefault();
        }
    } else if (id === 'del_quiz_inst') {
        let confirmed = confirm("Are you sure you want to delete this quiz?");
        if (!confirmed) {
            event.preventDefault();
        }
    } else if (id === 'del_quiz_ques') {
        let confirmed = confirm("Are you sure you want to delete this question?");
        if (!confirmed) {
            event.preventDefault();
        }
    } else if (id === 'del_quiz_sess') {
        let confirmed = confirm("Are you sure you want to delete this quiz session?");
        if (!confirmed) {
            event.preventDefault();
        }
    } else if (id === 'exit_quiz_sess') {
        let confirmed = confirm("Are you sure you want to leave this quiz?");
        if (!confirmed) {
            event.preventDefault();
        }  
    } else if (id === 'hide_quiz_inst') {
        let confirmed = confirm("Are you sure you want to hide this quiz?");
        if (!confirmed) {
            event.preventDefault();
        }               
    } else if (id === 'mark_complete') {
        let confirmed = confirm("Are you sure you want to mark this quiz as complete?");
        if (!confirmed) {
            event.preventDefault();
        }   
    } else {
        event.preventDefault();
    }
}

// Question creation: question type upload field
let questionTypeOption = document.getElementById('questionType');

let questionTypeImage = document.getElementById('questionImageField');
let questionTypeAudio = document.getElementById('questionAudioField');

if (questionTypeOption) {
    questionTypeOption.addEventListener('change', function() {
    
        switch (questionTypeOption.value) {
            case '1':
                questionTypeImage.style.display = 'none'
                questionTypeAudio.style.display = 'none'
                break;
            case '2':
                questionTypeImage.style.display = 'block'
                questionTypeAudio.style.display = 'none'
                break;
            case '3':
                questionTypeImage.style.display = 'none'
                questionTypeAudio.style.display = 'block'
                break;
            default:
                questionTypeImage.style.display = 'none'
                questionTypeAudio.style.display = 'none'
        }
    })
}


// Question creation: answer highlight
let selectOption = document.getElementById('questionAnswerSelect');

let answer1 = document.getElementById('questionAnswer1');
let answer2 = document.getElementById('questionAnswer2');
let answer3 = document.getElementById('questionAnswer3');
let answer4 = document.getElementById('questionAnswer4');

if (selectOption) {
    selectOption.addEventListener('change', function() {
    
        switch (selectOption.value) {
            case '1':
                answer1.style.backgroundColor = '#ABEBC6';
                answer2.style.backgroundColor = 'white';
                answer3.style.backgroundColor = 'white';
                answer4.style.backgroundColor = 'white';
                break;
            case '2':
                answer1.style.backgroundColor = 'white';
                answer2.style.backgroundColor = '#ABEBC6';
                answer3.style.backgroundColor = 'white';
                answer4.style.backgroundColor = 'white';
                break;
            case '3':
                answer1.style.backgroundColor = 'white';
                answer2.style.backgroundColor = 'white';
                answer3.style.backgroundColor = '#ABEBC6';
                answer4.style.backgroundColor = 'white';
                break;
            case '4':
                answer1.style.backgroundColor = 'white';
                answer2.style.backgroundColor = 'white';
                answer3.style.backgroundColor = 'white';
                answer4.style.backgroundColor = '#ABEBC6';
                break;
            default:
                answer1.style.backgroundColor = 'white';
                answer2.style.backgroundColor = 'white';
                answer3.style.backgroundColor = 'white';
                answer4.style.backgroundColor = 'white';
        }
    });

    // Manually triggers above code.
    selectOption.dispatchEvent(new Event('change'));
}



// Character count
function countCharacters(input, counter, number = 200) {
    let inputField = document.getElementById(input);
    let charCount = document.getElementById(counter);

    inputField.addEventListener('input', updateCounter);
    inputField.addEventListener('focus', updateCounter);
    inputField.addEventListener('blur', hideCounter);

    function updateCounter() {
        let inputValue = inputField.value;
        let count = inputValue.length;

        charCount.style.display = 'block';
        charCount.textContent = `Character count: ${count}/${number}`;

        number_int = parseInt(number, 10);

        if (count === number_int) {
            charCount.style.color = 'red';
        } else {
            charCount.style.color = '#333';
        }
    }

    function hideCounter() {
        charCount.style.display = 'none';
    }

    updateCounter();
}


function redirectToPage(url) {
    window.location.href = url;
  }