var updateBtns = document.getElementsByClassName('update-cart')

for(var i=0; i<updateBtns.length; i++ ){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        var max_quantity = parseInt(this.dataset.max_quantity)
        if(user == 'AnonymousUser'){
            addCookieItem(productId, action, max_quantity)
        }else{
            updateUserOrder(productId, action)
        }
    })
}
function addCookieItem(productId, action, max_quantity){
    if(action == 'add')
    {
        if(cart[productId] == undefined && max_quantity > 0)
        {
            cart[productId] = {'quantity': 1}
        }
        else if(parseInt(cart[productId]['quantity']) < max_quantity)
        {
            cart[productId]['quantity'] += 1
        }
    }

    if(action == 'remove')
    {
        cart[productId]['quantity'] -= 1

        if(cart[productId]['quantity'] <= 0)
        {
        delete cart[productId]
        }
    }

    document.cookie = 'cart=' + JSON.stringify(cart) +";domain=;path=/"
    location.reload()
}

function updateUserOrder(productId, action){
    var url ='/update_item/'

    // sending data to view
    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })

    .then((response) =>{return response.json()})

    .then((data) =>{
        location.reload()
     })


}

var login_out_Button = document.getElementById("login_out_Button");
var loginButton = document.getElementById("login-Button");
var user_profile_Button = document.getElementById("user-profile-Button");
function toggleLoginStatus() {
    if (user != 'AnonymousUser') {
        user_profile_Button.classList.remove("hidden");
        login_out_Button.innerText = "Wyloguj";
        login_out_Button.href = "/accounts/logout";
    } else {
        user_profile_Button.classList.add("hidden");
        login_out_Button.innerText = "Zaloguj";
        login_out_Button.href = "/accounts/login";
    }
}


if(loginButton != null){ loginButton.addEventListener('click', toggleLoginStatus()); }
else{ toggleLoginStatus(); }



var dropdown_buttons = document.getElementsByClassName('dropdown-button');
for(var i=0; i<dropdown_buttons.length; i++ ){
    dropdown_buttons[i].addEventListener('click', function(){
        var category = this.dataset.category
        var subcategory_div = document.getElementById(category)
        if(this.src.search("dropdown.png")!= -1)
        {
            subcategory_div.classList.remove("hidden");
            this.src = this.src.replace("dropdown.png", "dropup.png");
        }
        else
        {
            subcategory_div.classList.add("hidden");
            this.src = this.src.replace("dropup.png", "dropdown.png");
        }

    })
}
