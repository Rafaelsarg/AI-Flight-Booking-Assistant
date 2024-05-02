const sendMsgBtn = document.querySelector(".send-btn");
const restartBtn = document.querySelector(".reset-btn");
const msgInput = document.querySelector('.text-inp');
const chatbox = document.querySelector('.chatbox');
const bookingBox = document.querySelector('.bookings');

// FLIGHT ITINERARY POPUP WINDOW ELEMENTS
const itineraryPopupWindow = document.querySelector('.popup-itinerary');
const upperInfoBox = document.querySelector('.upper-info-box');
const inboundFlightInfoBox = document.querySelector('.mid-flight-info-box .inbound-flight-info-box');
const outboundFlightInfoBox = document.querySelector('.mid-flight-info-box .outbound-flight-info-box');
const closePopupBtn = document.querySelector('.closing-box .close-btn');

const overlay = document.querySelector('.overlay');

let userMessage;

const createMessage = (message, className) => {
    const messageLi = document.createElement('li');
    messageLi.classList.add("chat", className);
    messageLi.innerHTML = `<p>${message}</p>`;
    return messageLi;
}

const createTravelerNumInput = () => {
    const messageLi = document.createElement('li');
    const inputAdults = document.createElement('input');
    const inputKids = document.createElement('input');
    const inputInfants = document.createElement('input');
    const pAdults = document.createElement('p');
    const pKids = document.createElement('p');
    const pInfants = document.createElement('p');
    const submitBtn = document.createElement('input');


    inputAdults.setAttribute('type', 'number');
    inputAdults.setAttribute('value', 0);
    inputAdults.setAttribute('min', 0);
    inputAdults.setAttribute('class', 'input-adults-number');

    inputKids.setAttribute('type', 'number');
    inputKids.setAttribute('value', 0);
    inputKids.setAttribute('min', 0);
    inputKids.setAttribute('class', 'input-kids-number');

    inputInfants.setAttribute('type', 'number');
    inputInfants.setAttribute('value', 0);
    inputInfants.setAttribute('min', 0);
    inputInfants.setAttribute('class', 'input-infants-number');

    pAdults.innerHTML = 'Adults';
    pKids.innerHTML = 'Kids';
    pInfants.innerHTML = 'Infants';
    submitBtn.setAttribute('type', 'button');
    submitBtn.setAttribute('value', 'Submit');
    submitBtn.setAttribute('class', 'travelers-number-submit-btn');

    messageLi.classList.add("chat", 'travelers');
    messageLi.appendChild(pAdults);
    messageLi.appendChild(inputAdults);
    messageLi.appendChild(pKids);
    messageLi.appendChild(inputKids);
    messageLi.appendChild(pInfants);
    messageLi.appendChild(inputInfants);
    messageLi.appendChild(submitBtn);

    return messageLi;
}



const createFlightInfoBox = (data, key) => {
    const flightInfoBox = document.createElement('div');
    flightInfoBox.classList.add('flight-info-box');
    flightInfoBox.innerHTML = `
        <div class="origin-destination-codes">
            <div class="inb-outb-title">
                <h3>Inbound</h3>
            </div>
            <div class="sliding-info-block">
                <div class="origin-code-time">
                    <span class="time">
                        ${data['departure']['hour']}:${data['departure']['minute'] < 10 ? '0' + data['departure']['minute']  : data['departure']['minute']}
                    </span>
                    <span>${data['origin']}</span>
                </div>
                <div class="line-container">
                    <div class="duration"><span>${data['duration']['hour'] + 'H' + ' ' + data['duration']['minute'] + 'M'}</span></div>
                    <div class="line"></div>
                    <div class="stops">${data['stops']} ${data['stops'] === 1 ? 'stop' : 'stops'}</div>
                </div>
                <div class="destination-code-time">
                    <span class="time">
                    ${data['arrival']['hour']}:${data['arrival']['minute'] < 10 ? '0' + data['arrival']['minute']  : data['arrival']['minute']}
                    </span>
                    <span>${data['destination']}</span>
                </div>
            </div>
        </div>
        <div class="info-book-block">
            <div class="duration-itinerary">
                <div class="price-currency">
                    <span>Price ${data['price'] + ' ' + data['currency']}</span>
                </div>
                <div class="itinerary-link">
                    <a href="#" class="itinerary-popup-link ${key}">See itinerary details</a>
                </div>
            </div>
            <div class="book-flight-block">
                <button class="select-button ${key}">SELECT</button>
            </div>
        </div>
    `;

    return flightInfoBox;
}

const createSingleFlightInfoBox = (data) => {
    const flightInfoBox = document.createElement('div');
    flightInfoBox.classList.add('single-flight-info-block');
    flightInfoBox.innerHTML = `
        <span>Duration: ${data['duration']['hour'] + 'H' + ' ' + data['duration']['minute'] + 'M'}</span>
        <span>Departure: <b>${data['departure']['at']['hour']}:${data['departure']['at']['minute'] < 10 ? '0' + data['departure']['at']['minute']  : data['departure']['at']['minute']}  ${data['departure']['iataCode']}</b></span>
        <span>Arrival: <b>${data['arrival']['at']['hour']}:${data['arrival']['at']['minute'] < 10 ? '0' + data['arrival']['at']['minute']  : data['arrival']['at']['minute']} ${data['arrival']['iataCode']}</b></span>
    `;

    return flightInfoBox;
}

const createTotalDuration = (data) => {
    const durationBox = document.createElement('div');
    durationBox.classList.add('total-duration');

    durationBox.innerHTML = `
        <span>Total duration: ${data['hour'] + 'H' + ' ' + data['minute'] + 'M'}</span>
    `;

    return durationBox;
}

const creteFlightItineraryBlock = (data) => {
    const flightItineraryBlock = document.createElement('div');
    flightItineraryBlock.classList.add('flight-itinerary-block');

    for (const flight of data) {
        flightItineraryBlock.appendChild(createSingleFlightInfoBox(flight));
    }

    return flightItineraryBlock;
}

const createItineraryPopup = (data) => {
    const header = document.createElement('h1');
    header.innerHTML = `${data['origin']} - ${data['destination']}`;
    upperInfoBox.innerHTML = '';
    upperInfoBox.appendChild(header);

    inboundFlightInfoBox.innerHTML = '';
    inboundFlightInfoBox.innerHTML += `
        <h1>Inbound Flight</h1>
        <span>Departs on ${data['departure']['day']}-${data['departure']['month']}-${data['departure']['year']}</span>
        <span>Arrives on ${data['arrival']['day']}-${data['arrival']['month']}-${data['arrival']['year']}</span>
    `;

    inboundFlightInfoBox.appendChild(createTotalDuration(data['duration']));
    inboundFlightInfoBox.appendChild(creteFlightItineraryBlock(data['segments']));

    if(data['return'] !== undefined) {
        outboundFlightInfoBox.innerHTML = '';
        outboundFlightInfoBox.innerHTML += `
            <h1>Outbound Flight</h1>
            <span>Departs on ${data['return_departure']['day']}-${data['departure']['month']}-${data['departure']['year']}</span>
            <span>Arrives on ${data['return_arrival']['day']}-${data['arrival']['month']}-${data['arrival']['year']}</span> 
         `;
        
        outboundFlightInfoBox.appendChild(createTotalDuration(data['return_duration']));
        outboundFlightInfoBox.appendChild(creteFlightItineraryBlock(data['return']));
    }

}

const handleTravelersNum = () => {
    const adultsNum = document.querySelector('.input-adults-number').value;
    const kidsNum = document.querySelector('.input-kids-number').value;
    const infantsNum = document.querySelector('.input-infants-number').value;

    if (adultsNum <= 0 && kidsNum <= 0 && infantsNum <= 0) {
        alert('Please enter a valid number of travelers');
        return;
    }
    if (adultsNum < infantsNum) {
        alert('Please enter a valid number of travelers, infants cannot be more than adults');
        return;
    }

    bookingBox.innerHTML = '<h1>Please wait for the results...</h1>';
    $.ajax({
        url: '/travelersnum',
        type: 'POST',
        data: JSON.stringify({ 'adults_num': adultsNum, 'kids_num': kidsNum, 'infants_num': infantsNum }),
        contentType: "application/json",
        dataType: 'json',
        success: function (data) {
            if(data.dialogueEnd == true){
                bookingBox.innerHTML = '';
                chatbox.appendChild(createMessage(data.system_response, 'incoming'));
                return;
                return
            }


            chatbox.appendChild(createMessage(data.system_response, 'incoming'));
            const keys = Object.keys(data.flight_data);
            bookingBox.innerHTML = '';
            for (const key of keys) {
                bookingBox.appendChild(createFlightInfoBox(data.flight_data[key], key));
                const itineraryLink = document.querySelector(`.itinerary-popup-link.${key}`);
                itineraryLink.addEventListener('click', () => handleBookings(key));
            }
            

        }
    });
}

const handleChat = () => {
    userMessage = msgInput.value.trim();
    const formData = new FormData();
    if(!userMessage) return;
    chatbox.appendChild(createMessage(userMessage, 'outgoing'));

    $.ajax({
        url: '/get',
        type: 'POST',
        data: JSON.stringify({ 'usrMessage': userMessage }),
        contentType: "application/json",
        dataType: 'json',
        success: function (data) {
            chatbox.appendChild(createMessage(data.system_response, 'incoming'));
            if (data.dialogueEnd == true){
                return
            }
            if (data.travelersNumberInquiry == true) {
                chatbox.appendChild(createTravelerNumInput());
                const travelersNumSubmitBtn = document.querySelector('.travelers-number-submit-btn');;
                travelersNumSubmitBtn.addEventListener('click', handleTravelersNum);
            }
        },
    });
    msgInput.value = '';
}

const handleRestart = () => {
    $.ajax({
        url: '/restart',
        type: 'POST',
        contentType: "application/json",
        dataType: 'json',
        success: function (data) {
            chatbox.innerHTML = '';
            bookingBox.innerHTML = '';
            chatbox.appendChild(createMessage('Hello! I am an AI-trained chatbot here to assist you with booking your upcoming flight. To ensure a smooth booking process, kindly answer the questions I will provide. Lets begin with the details of your flights origin and destination. Could you please provide me with these details?', 'incoming'));
        }
    });
}

handleBookings = (key) => {
    $.ajax({
        url: '/flight-itinerary',
        type: 'POST',
        data: JSON.stringify({ 'key': key }),
        contentType: "application/json",
        dataType: 'json',
        success: function (data) {
            itineraryPopupWindow.style.display = 'flex';
            overlay.style.display = 'block';
            createItineraryPopup(data);
        }
    });
}

closePopupBtn.addEventListener('click', () => {
    itineraryPopupWindow.style.display = 'none';
    overlay.style.display = 'none';
});

sendMsgBtn.addEventListener('click', handleChat);
restartBtn.addEventListener('click', handleRestart);