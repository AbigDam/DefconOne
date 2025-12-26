//Sliders Set up
var slider = document.getElementById("amount");
var output = document.getElementById("amount_label");
output.innerHTML = "Amount: " + slider.value;

slider.oninput = function() {
    output.innerHTML = "Amount: " + slider.value;
}

//Battle Sliders
var div_attack_slider = document.getElementById("div_attack");
var div_attack_output = document.getElementById("div_attack_label");
div_attack_output.innerHTML = "Amount: " + div_attack_slider.value;
div_attack_slider.oninput = function () {
    div_attack_output.innerHTML = "Amount: " + this.value;
};

var boat_attack_slider = document.getElementById("boat_attack");
var boat_attack_output = document.getElementById("boat_attack_label");
boat_attack_output.innerHTML = "Amount: " + boat_attack_slider.value;
boat_attack_slider.oninput = function () {
    boat_attack_output.innerHTML = "Amount: " + this.value;
};

var planes_attack_slider = document.getElementById("planes_attack");
var planes_attack_output = document.getElementById("planes_attack_label");
planes_attack_output.innerHTML = "Amount: " + planes_attack_slider.value;
planes_attack_slider.oninput = function () {
    planes_attack_output.innerHTML = "Amount: " + this.value;
};


document.addEventListener("DOMContentLoaded", function() {
    const states = parseInt("{{ PlayerAAA.states }}") || 0;
    const maxTier = 250;
    const bar = document.getElementById("dev-bar");

    // Clamp states to a max of 250 for the visual bar
    const progress = Math.min(states, maxTier) / maxTier * 100;
    bar.style.width = progress + "%";
});


const openShopBtn = document.getElementById("openShopBtn");
const closeShopBtn = document.getElementById("closeShopBtn");
const shopOverlay = document.getElementById("shopOverlay");

openShopBtn.addEventListener("click", () => {
    shopOverlay.style.display = "flex";
});

closeShopBtn.addEventListener("click", () => {
    shopOverlay.style.display = "none";
});

// Close when clicking the dark background
shopOverlay.addEventListener("click", (e) => {
    if (e.target === shopOverlay) {
        shopOverlay.style.display = "none";
    }
});


const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = 1120;
canvas.height = 480;
const colorDisplay = document.getElementById('colorDisplay');

const overlay = document.getElementById('overlayCanvas');
const ctxO = overlay.getContext('2d');

overlay.addEventListener('click', function(event) {

    const rect = overlay.getBoundingClientRect();
    
    // Correct for any scaling
    const scaleX = overlay.width / rect.width;
    const scaleY = overlay.height / rect.height;
    
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    // Wipe ONLY the overlay canvas (keeps tiles visible underneath)
    ctxO.clearRect(0, 0, overlay.width, overlay.height);
    if (stateToggle.checked) {
        // Draw the new circle
        ctxO.beginPath();
        ctxO.arc(x, y, 10, 0, Math.PI * 2);
        ctxO.fillStyle = "rgba(255, 0, 0, 0.6)";
        ctxO.fill();
        ctxO.strokeStyle = "red";
        ctxO.lineWidth = 2;
        ctxO.stroke();
    }
});

const bottom = document.getElementById('canvas');
stateToggle = document.getElementById("stateToggle");

overlay.addEventListener('click', function(event) {
    // 1. Draw the circle on top
    const rect = overlay.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // (Circle drawing code here...)

    // 2. Manually trigger the click on the bottom canvas
    const simulatedClick = new MouseEvent('click', {
        clientX: event.clientX,
        clientY: event.clientY,
        bubbles: true,
        cancelable: true
    });
    
    bottom.dispatchEvent(simulatedClick);
});

const img = new Image();
img.onload = () => {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    document.getElementById('loading').style.display = 'none';
    document.getElementById('canvasContainer').style.display = 'block';
}};
img.crossOrigin = "anonymous"; 
const gameId = '{{ game_id }}';
img.src = `{{path}}`;


let refreshed = false;

const ws = new WebSocket(
  "ws://" + window.location.host + "/ws/refresh/"
);

ws.onmessage = () => {
  if (refreshed) return;
  refreshed = true;
  location.reload();
};


const tileCanvases = [];

async function loadTiles() {
  await Promise.all(
    window.TILES.map((relPath) => {
      return new Promise((resolve) => {
        const img = new Image();
        img.src = `/static/${relPath}`;
        img.onload = () => {
          const canvas = document.createElement("canvas");
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0);
          tileCanvases.push({ name: relPath, ctx });
          resolve();
        };
      });
    })
  );
}

loadTiles();

const map = document.getElementById("canvas");
const stateToggle = document.getElementById("stateToggle");
const frontName = document.getElementById('frontName');
const frontNameInput = document.getElementById('frontNameInput');


map.addEventListener("click", (e) => {
    
  if (!stateToggle.checked) {
    frontName.textContent = "";
    frontNameInput.value = "";
    return
  }
  const rect = map.getBoundingClientRect();
  const x = Math.floor(e.clientX - rect.left);
  const y = Math.floor(e.clientY - rect.top);

  for (const tile of tileCanvases) {
    const alpha = tile.ctx.getImageData(x, y, 1, 1).data[3];
    if (alpha > 0) {
      var clean =  tile.name.replace("AWSDefcon1App/white_image/MapChart_Map.", "").replace(/\.png$/, "");
      frontName.textContent = clean + " front";
      break;
    }
  }

  frontNameInput.value = frontName.textContent

});

            const colors = {
                'Ocean': '#000000',
                'United Kingdom': '#ff4879',
                'Soviet Union': '#a3101f',
                'Italy': '#56a552',
                'Brazil': '#62bd52',
                'Sultanate of Aussa': '#08c237',
                'Turkey': '#c7e9b4',
                'Norway': '#623c3c',
                'Iraq': '#e79481',
                'Saudi Arabia': '#def7c6',
                'United States': '#57a1ff',
                'Albania': '#c23b85',
                'Canada': '#9b3e33',
                'France': '#4892FF',
                'Kingdom of Hungary': '#ffa47f',
                'China': '#dfe5a0',
                'Chile': '#ca828b',
                'Peru': '#fff6ff',
                'British Raj': '#c80a0a',
                'Spain': '#ffff79',
                'Kingdom of Greece': '#79ebff',
                'Lithuania': '#ffff9b',
                'Mexico': '#86c66c',
                'Ethiopia': '#c3a5f5',
                'Romania': "#9e9e00", 
                'Portugal': '#33965b',
                'Bhutan': '#ac7a58',
                'Poland': '#ff7789',
                'Australia': '#49bb7e',
                'Czechoslovakia': '#46d8cb',
                'Sweden': '#2eadff',
                'Venezuela': "#70b626", 
                'Yugoslavia': '#5e5ea4',
                'Netherlands': '#ffb35f',
                'German Reich': '#525252',
                'Bulgaria': '#329a00',
                'Belgium': '#fbdf0a',
                'South Africa': '#be96fa',
                'Philippines': '#b496e6',
                'Uruguay': '#abbe99',
                'Argentina': '#bdccff',
                'Republic of Paraguay': '#4696fa',
                'Mengkukuo': '#a5e684',
                'Japan': '#fee8c8',
                'Ireland': '#68cf75',
                'Costa Rica': '#927a30',
                'Cuba': '#8b40a6',
                'Colombia': '#fff375',
                'Sinkiang': '#3fb08d',
                'Yunnan': '#698948',
                'Dominican Republic': '#bea0f0',
                'Mongolia': '#5a771d',
                'Switzerland': '#c15151',
                'Ecuador': '#ffbe7f',
                'El Salvador': '#fabe78',
                'Iran': '#5c927e',
                'Xibei San Ma': '#685b84',
                'Denmark': "#e25c0e", 
                'Guangxi Clique': '#8a9a74',
                'Guatemala': '#473070',
                'Haiti': '#ab6f72',
                'Finland': '#ffffff',
                'Estonia': '#63cdfe',
                'Manchukuo': '#ff7847',
                'Afghanistan': '#53d0d9',
                'Honduras': "#B6E01F", 
                'Iceland': '#c79779',
                'Siam': '#d7f0c8',
                'Dutch East Indies': "#5b21e2", 
                'Latvia': '#7b7cb8',
                'Bolivian Republic': '#ffeab1',
                'Liberia': '#cdafff',
                'Austria': "#a999f0", 
                'Luxembourg': '#8adba2',
                'Tibet': '#456722',
                'Nepal': '#c8aafa',
                'Nicaragua': '#92b2bf',
                'British Malaya': "#e623d5", 
                'New Zealand': '#b99beb',
                'Oman': '#905c5c', 
                'Shanxi': '#651e29',
                'Panama': '#9e8add',
                'Communist China': '#b2233b',
                'Tannu Tuva': "#e94a4a",
                'Yemen': '#905d5d',
            }
        const hexToRgb = (hex) => {
            const bigint = parseInt(hex.slice(1), 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `rgb(${r}, ${g}, ${b})`;
        };
        const rgbToCountry = {};
        for (const country in colors) {
            const rgbColor = hexToRgb(colors[country]);
            rgbToCountry[rgbColor] = country;
        }

    window.addEventListener('DOMContentLoaded', () => {
        const country = localStorage.getItem('selectedCountry');
        const nationSelect = document.getElementById('nationSelect');
        // Check if the country is still a valid option
        const isCountryValid = [...nationSelect.options].some(
            option => option.value === country
        );

        if (country && isCountryValid) {
            const frontName = document.getElementById('frontName');
            const frontNameInput = document.getElementById('frontNameInput');
            frontName.textContent = "";
            frontNameInput.value = "";
            
            colorDisplay.textContent = `${country}`;
            offerDisplay.textContent = `Offer Alliance to ${country}`;
            sendText.textContent = `Send Supplies to ${country}`; 

            var some_var = "{{ nation_name_at_war }}";
            nationsAtWar = some_var.replaceAll("&#x27;", "");
            var playerA = "{{PlayerAAA.name}}"
            console.log(playerA);
            if (!nationsAtWar.includes(country)) {
                document.getElementById("battle-form").style.display = "none";
                document.getElementById('div1').style.display = "none";
                document.getElementById('div2').style.display = "none";
                document.getElementById('showDiv1').style.display = "none";
                document.getElementById('showDiv2').style.display = "none";
                if(playerA != country && "Ocean" != country){
                    document.getElementById('peace-form').style.display = "block";
                    const warInput = document.getElementById('war-input');
                    const allianceInput = document.getElementById('alliance-input');
                    const sendInput = document.getElementById('send-input');
                    warInput.value = country;
                    sendInput.value = country;
                    allianceInput.value = country;
                }
                if(playerA == country || "Ocean" == country){
                    document.getElementById('peace-form').style.display = "none";
                    offerHostility.textContent = `No Hostility`;
                    stateCount.textContent = `(not divided into states)`;
                }
                
            } else {
                document.getElementById("battle-form").style.display = "block";
                document.getElementById('showDiv1').style.display = "inline-block";
                document.getElementById('showDiv2').style.display = "inline-block";
                document.getElementById('atWar').style.display = "inline-block";
                document.getElementById('peace-form').style.display = "none";
                const victimInput = document.getElementById('victim-input');
                const defenderInput = document.getElementById('defender-input');
                defenderInput.value = country;
                victimInput.value = country;
            }

            console.log("Starting Next Part");
            // Get the table element
            // JavaScript variable 'country' (set this value dynamically)

            // Get the table element and its rows
            const stateCount = document.getElementById('stateCount');
            const filter = country.toLowerCase(); // Convert country to lowercase for case-insensitive comparison
            const nationsTable = document.getElementById('nationsTable'); // Reference the table element
            const rows = nationsTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr'); // Get all rows from the table body
            // Loop through each row in the table
            for (const row of rows) {
                const name = row.cells[0].textContent.toLowerCase(); // Get text content from the 2nd column (index 1) and convert to lowercase

                if (name === filter) {
                    offerHostility.textContent = `Hostility: ${row.cells[5].textContent.toLowerCase()}`;
                    stateCount.textContent = `(States: ${row.cells[1].textContent.toLowerCase()})`;

                } else {
                    row.style.display = "none"; // Hide non-matching rows
                }
            }

            // Make the table visible if at least one row matches
            nationsTable.style.display = "table";
        }
    });

    document.getElementById('nationForm').addEventListener('submit', function(event) {
            const frontName = document.getElementById('frontName');
            const frontNameInput = document.getElementById('frontNameInput');
            frontName.textContent = "";
            frontNameInput.value = "";

            event.preventDefault();  
            const country = document.getElementById('nationSelect').value;
            localStorage.setItem('selectedCountry', country);
            console.log(`Closest color name: ${country}`);
            
            colorDisplay.textContent = `${country}`;
            offerDisplay.textContent = `Offer Alliance to ${country}`;
            sendText.textContent = `Send Supplies to ${country}`; 

            var some_var = "{{ nation_name_at_war }}";
            nationsAtWar = some_var.replaceAll("&#x27;", "");
            var playerA = "{{PlayerAAA.name}}"
            console.log(playerA);
            if (!nationsAtWar.includes(country)) {
                document.getElementById("battle-form").style.display = "none";
                document.getElementById('div1').style.display = "none";
                document.getElementById('div2').style.display = "none";
                document.getElementById('showDiv1').style.display = "none";
                document.getElementById('showDiv2').style.display = "none";
                if(playerA != country && "Ocean" != country){
                    document.getElementById('peace-form').style.display = "block";
                    const warInput = document.getElementById('war-input');
                    const allianceInput = document.getElementById('alliance-input');
                    const sendInput = document.getElementById('send-input');
                    warInput.value = country;
                    sendInput.value = country;
                    allianceInput.value = country;
                }
                if(playerA == country || "Ocean" == country){
                    document.getElementById('peace-form').style.display = "none";
                    offerHostility.textContent = `No Hostility`;
                    stateCount.textContent = `(not divided into states)`;
                }
                
            } else {
                document.getElementById("battle-form").style.display = "block";
                document.getElementById('showDiv1').style.display = "inline-block";
                document.getElementById('showDiv2').style.display = "inline-block";
                document.getElementById('atWar').style.display = "inline-block";
                document.getElementById('peace-form').style.display = "none";
                const victimInput = document.getElementById('victim-input');
                const defenderInput = document.getElementById('defender-input');
                defenderInput.value = country;
                victimInput.value = country;
            }

            console.log("Starting Next Part");
            // Get the table element
            // JavaScript variable 'country' (set this value dynamically)

            // Get the table element and its rows
            
            const filter = country.toLowerCase(); // Convert country to lowercase for case-insensitive comparison
            const nationsTable = document.getElementById('nationsTable'); // Reference the table element
            const offerHostility = document.getElementById('offerHostility');
            const rows = nationsTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr'); // Get all rows from the table body
            // Loop through each row in the table
            for (const row of rows) {
                const name = row.cells[0].textContent.toLowerCase(); // Get text content from the 2nd column (index 1) and convert to lowercase


                if (name === filter) {
                    offerHostility.textContent = `Hostility: ${row.cells[5].textContent.toLowerCase()}`;
                    stateCount.textContent = `(States: ${row.cells[1].textContent.toLowerCase()})`;
                } else {
                    row.style.display = "none"; // Hide non-matching rows
                }
            }

            nationsTable.style.display = "none";

        });

        canvas.addEventListener('click', (event) => {
            const { offsetX, offsetY } = event;
            const imageData = ctx.getImageData(offsetX, offsetY, 1, 1).data;
            const rgb = [imageData[0], imageData[1], imageData[2]]; // Convert to array for distance calculation

            // Initialize variables for tracking the closest color
            var closestColorName = null;
            var smallestDistance = Infinity;

            // Iterate over the dictionary to find the closest color
            for (const [colorRgb, colorName] of Object.entries(rgbToCountry)) {

                const colorRgbArray = colorRgb
                .replace("rgb(", "")  // Remove "rgb("
                .replace(")", "")    // Remove ")"
                .split(",")          // Split on commas
                .map(Number);        // Convert to numbers
                const distance = Math.sqrt(
                    Math.pow(rgb[0] - colorRgbArray[0], 2) +
                    Math.pow(rgb[1] - colorRgbArray[1], 2) +
                    Math.pow(rgb[2] - colorRgbArray[2], 2)
                );


                if (distance < smallestDistance) {
                    smallestDistance = distance;
                    closestColorName = colorName;
                }
            }
            const country = closestColorName;
            localStorage.setItem('selectedCountry', country);
            colorDisplay.textContent = `${country}`;
            offerDisplay.textContent = `Offer Alliance to ${country}`;
            sendText.textContent = `Send Supplies to ${country}`; 

        var some_var = "{{ nation_name_at_war }}";
        nationsAtWar = some_var.replaceAll("&#x27;", "");
        var playerA = "{{PlayerAAA.name}}"
        if (!nationsAtWar.includes(country)) {
            document.getElementById("battle-form").style.display = "none";
            document.getElementById('div1').style.display = "none";
            document.getElementById('div2').style.display = "none";
            document.getElementById('showDiv1').style.display = "none";
            document.getElementById('showDiv2').style.display = "none";
            if(playerA != country && "Ocean" != country){
                document.getElementById('peace-form').style.display = "block";
                const warInput = document.getElementById('war-input');
                const allianceInput = document.getElementById('alliance-input');
                const sendInput = document.getElementById('send-input');
                warInput.value = country;
                sendInput.value = country;
                allianceInput.value = country;
            }
            if(playerA == country || "Ocean" == country){
                document.getElementById('peace-form').style.display = "none";
                offerHostility.textContent = `No Hostility`;
                stateCount.textContent = `(not divided into states)`;
            }
            
        } else {
            document.getElementById("battle-form").style.display = "block";
            document.getElementById('showDiv1').style.display = "inline-block";
            document.getElementById('showDiv2').style.display = "inline-block";
            document.getElementById('atWar').style.display = "inline-block";
            document.getElementById('peace-form').style.display = "none";
            const victimInput = document.getElementById('victim-input');
            const defenderInput = document.getElementById('defender-input');
            defenderInput.value = country;
            victimInput.value = country;
        }

        console.log("Starting Next Part");
        // Get the table element
        // JavaScript variable 'country' (set this value dynamically)

        // Get the table element and its rows
        
        const filter = country.toLowerCase(); // Convert country to lowercase for case-insensitive comparison
        const nationsTable = document.getElementById('nationsTable'); // Reference the table element
        const rows = nationsTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr'); // Get all rows from the table body

        // Loop through each row in the table
        for (const row of rows) {
            const name = row.cells[0].textContent.toLowerCase(); // Get text content from the 2nd column (index 1) and convert to lowercase

            if (name === filter) {
                offerHostility.textContent = `Hostility: ${row.cells[5].textContent.toLowerCase()}`;
                stateCount.textContent = `(States: ${row.cells[1].textContent.toLowerCase()})`;
            } else {
                row.style.display = "none"; // Hide non-matching rows
            }
        }

        // Make the table visible if at least one row matches
        nationsTable.style.display = "table";

        });

        document.addEventListener('DOMContentLoaded', () => {
            // Get buttons and divs
            const button1 = document.getElementById('showDiv1');
            const button2 = document.getElementById('showDiv2');
            const div1 = document.getElementById('div1');
            const div2 = document.getElementById('div2');
            const battleForm = document.getElementById('battle-form');

            // Ensure battle form is visible
            battleForm.style.display = 'block';

            // Show Div 1 and hide Div 2
            button1.addEventListener('click', () => {
                div1.style.display = 'block';
                div2.style.display = 'none';
            });

            // Show Div 2 and hide Div 1
            button2.addEventListener('click', () => {
                div2.style.display = 'block';
                div1.style.display = 'none';
            });
        });
            document.addEventListener('DOMContentLoaded', () => {
        
                const gifPath = '/static/AWSDefcon1App/Loading_Battle.gif';
                const gifContainer = document.createElement('div');
                const gifImage = document.createElement('img');
        
                // Styling for the gif container
                gifContainer.style.position = 'fixed';
                gifContainer.style.top = '0';
                gifContainer.style.left = '0';
                gifContainer.style.width = '100%';
                gifContainer.style.height = '100%';
                gifContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';  // Semi-transparent black background
                gifContainer.style.display = 'none';  // Hidden initially
                gifContainer.style.justifyContent = 'center';
                gifContainer.style.alignItems = 'center';
                gifContainer.style.zIndex = '9999';  // Ensure it appears above all content
        
                // Setting up the gif image
                gifImage.src = gifPath;
                gifImage.style.maxWidth = '90%';
                gifImage.style.maxHeight = '90%';
        
                gifContainer.appendChild(gifImage);
                document.body.appendChild(gifContainer);
        
                // Event listener for clicks and form submissions
                document.addEventListener('click', (event) => {
                    const target = event.target;
                    if (target.classList.contains('attacker') || target.closest('button.attacker')) {
                        gifContainer.style.display = 'flex';
                        
                        // Automatically hide the gif after a certain duration
                        setTimeout(() => {
                            gifContainer.style.display = 'none';
                        }, 2000000);  
                    }
                });
        
                // Event listener specifically for form submissions
                document.addEventListener('submit', (event) => {
                    const target = event.target;
                    if (target.classList.contains('attacker')) {
                        gifContainer.style.display = 'flex';
    
                    }
                });
        

            });

document.querySelector('.qa-toggle-button').addEventListener('click', function() {
const container = document.querySelector('.qa-container');
container.style.display = (container.style.display === 'none' || container.style.display === '') ? 'block' : 'none';
});

document.querySelector('.qa-close').addEventListener('click', function() {
  document.querySelector('.qa-container').style.display = 'none';
});

const questions = document.querySelectorAll('.qa-question');
questions.forEach(q => {
  q.addEventListener('click', function() {
    const answer = this.nextElementSibling;

    // Hide all answers
    document.querySelectorAll('.qa-answer').forEach(a => a.style.display = 'none');

    // Toggle this one
    answer.style.display = 'block';
  });
});