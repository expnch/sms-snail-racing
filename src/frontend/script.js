// Overlays
function drawCheer(text) {
    let cheer = document.createElement('div');
    cheer.textContent = text;
    cheer.style.marginLeft = (Math.random() * canvas_w) + "px";
    cheer.style.marginTop = (Math.random() * canvas_h) + "px";
    cheer.classList.add('cheer');
    document.getElementById('overlay').prepend(cheer);
}

function drawAnnouncement(text, type='short') {
    let announce = document.createElement('div');
    announce.textContent = text;
    announce.style.width = "100%";
    announce.style.textAlign = 'center';
    announce.style.marginTop = '100px';
    announce.style.marginLeft = '100px';
    if (type == 'long') {
      announce.classList.add('announcement-long');
    } else { 
      announce.classList.add('announcement');
    }
    document.getElementById('overlay').prepend(announce);
}

// Game canvas
var canvas_w = 1200;
var canvas_h = 600;

var starting_line_x = 50;
var finish_line_x = 1100;

var goal_units = 60;

var Snail = function(x, y, color) {
  this.x = x;
  this.y = y;
  this.color = color;
};

var snail_w = 150;
var snail_h = 120;

var snail_0 = new Snail(starting_line_x, 35, 'rgba(255, 0, 255, 0.5)');
var snail_1 = new Snail(starting_line_x, 240, 'rgba(0, 153, 255, 0.5)');
var snail_2 = new Snail(starting_line_x, 445, 'rgba(255, 165, 0, 0.5)');
var snails = [snail_0, snail_1, snail_2];

var ctx;

var snail_img = new Image();
var checker = new Image();
snail_img.src = 'snail.gif';
checker.src = 'https://freepngimg.com/thumb/finish_line/26669-1-finish-line-hd.png';

window.onload = function() {
  ctx = document.getElementById('game').getContext('2d');
  
  window.requestAnimationFrame(drawBackground);
  window.requestAnimationFrame(drawSnailTrails);
  window.requestAnimationFrame(drawSnails);
}

function drawBackground() {
  ctx.save();
  // Starting line
  ctx.fillStyle = 'rgb(200, 0, 0)';
  ctx.fillRect(200, 0, 5, canvas_h);

  // Starting boxes
  ctx.fillStyle = snail_0.color;
  ctx.fillRect(70, 45, 100, 100);
  ctx.fillStyle = snail_1.color;
  ctx.fillRect(70, 250, 100, 100);
  ctx.fillStyle = snail_2.color;
  ctx.fillRect(70, 455, 100, 100);

  // Names
  ctx.fillStyle = 'rgba(0, 0, 0, 1.0)';
  ctx.font = '32px serif';
  ctx.fillText('Wanda', 70, 42);
  ctx.fillText('Yorick', 75, 245);
  ctx.fillText('Zippy', 80, 450);

  // Finish line
  ctx.restore();
  ctx.save();
  ctx.rotate(Math.PI/2);
  ctx.drawImage(checker, 0, -1350);
  ctx.restore();
}

function drawSnails() {
  for (let snail of snails) {
    ctx.save();
    ctx.drawImage(snail_img, snail.x, snail.y, snail_w, snail_h);
    ctx.restore();
  }
}

function drawSnailTrails() {
  for (let snail of snails) {
    if (snail.x > 200) {
      ctx.save();
      ctx.strokeStyle = snail.color;
      ctx.beginPath();
      ctx.moveTo(210, snail.y + (0.5 * snail_h));
      ctx.lineTo(snail.x + (0.5*snail_w), snail.y + (0.5 * snail_h));
      ctx.stroke();
      ctx.restore();
    }
  }
}

// Sockets
let socket = new WebSocket("ws://localhost:6789");

socket.onopen = function(e) {
  console.log("[open] WebSocket connection established");
};

socket.onmessage = function(event) {
  let event_json = JSON.parse(event.data);
  if (event_json.type == "cheer") {
    console.log('[event] Got a cheer', event_json.body);
    drawCheer(event_json.body); 
  } else if (event_json.type == "announcement") {
    console.log('[event] Got an announcment', event_json.body);
    drawAnnouncement(event_json.body); 
  } else if (event_json.type == "announcement-long") {
    console.log('[event] Got an announcment', event_json.body);
    drawAnnouncement(event_json.body, type='long'); 
  } else if (event_json.type == "move") {
    let array = event_json.body.split(',')
    snail_0.x = array[0]/goal_units * (finish_line_x - starting_line_x) + starting_line_x;
    snail_1.x = array[1]/goal_units * (finish_line_x - starting_line_x) + starting_line_x;
    snail_2.x = array[2]/goal_units * (finish_line_x - starting_line_x) + starting_line_x;
    console.log('[event] Position update: '+snail_0.x);
    ctx.clearRect(0,0,canvas_w,canvas_h);
    window.requestAnimationFrame(drawBackground);
    window.requestAnimationFrame(drawSnailTrails);
    window.requestAnimationFrame(drawSnails);
  }
}

socket.onclose = function(event) {
  if (event.wasClean) {
    console.log(`[close] Websockets connection closed cleanly, code=${event.code} reason=${event.reason}`);
  } else {
    console.log('[close] WebSockets connection died');
  }
  alert("Connection to server lost.")
};

socket.onerror = function(error) {
  console.log(`[error] ${error.message}`);
};

