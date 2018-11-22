var zerorpc = require('zerorpc');


var client = new zerorpc.Client({timeout: 5});
client.connect("tcp://127.0.0.1:8679");
client.invoke("PING", Date.now(), function(error, res, more) {
    if(res!='PONG'){
		console.log('Starting ML Prediction server');
		require("child_process").spawn('python',["./data/predict.py"]);
    }else{
		console.log('ML server: OK');
    }
});

module.exports = client;