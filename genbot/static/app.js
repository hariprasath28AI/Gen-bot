
class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send-btn')
        }

        this.waitEffect = false;
        this.state = false;
        this.messages = [{name: 'Blue', message: "Hi, I'm Mr. Blue, your personal assistant. How can I help you?"}];
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value;
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);


        fetch('http://0.0.0.0:80/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(data => {
            let msg2 = { name: "Blue", message: data.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = '';
        })
        .catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox);
            textField.value = '';
        });
    }


    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        textField.value = '';
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);
        this.waitEffect = true;
        this.updateChatText(chatbox)

        fetch('http://0.0.0.0:80/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Blue", message: r.answer };
            this.messages.push(msg2);
            this.waitEffect = false;
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.waitEffect = false;
            this.updateChatText(chatbox)
            textField.value = ''
          });
    }

    waitEffect(chatbox) {
        

    }

    updateChatText(chatbox) {
        var html = '';
        var waitbar = '<div class="messages-visitor-container"><img src="static\\images\\logo-with-bg.png" alt="ChatBot"><div class="messages__item messages__item--visitor"><lottie-player src="https://lottie.host/81902cb0-b2b6-400e-9847-c7721d400fd4/s1mSXofmec.json" background="transparent" speed="1" style="width: 60px; height: 60px;" loop autoplay></lottie-player></div></div>';
        if (this.waitEffect) {
            html += waitbar;
        }
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Blue")
            {
                html += '<div class="messages-visitor-container"><img src="static\\images\\logo-with-bg.png" alt="ChatBot"><div class="messages__item messages__item--visitor">' + item.message + '</div></div>'
            }
            else
            {
                html += '<div class="messages-operator-container"><div class="messages__item messages__item--operator">' + item.message + '</div><img src="static\\images\\User-logo.png" alt="User"></div>'
            }
          });
        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


const chatbox = new Chatbox();
chatbox.updateChatText(chatbox.args.chatBox);
chatbox.display();

let startbtn = document.getElementById("bot");
let closebtn = document.getElementById("close");

startbtn.addEventListener("click", function() {
    startbtn.style.display = "none";
    closebtn.style.display = "block";
});

closebtn.addEventListener("click", function() {
    startbtn.style.display = "block";
    closebtn.style.display = "none";
});
