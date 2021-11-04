// const http = require('http');

// const server = http.createServer(function(req,res){
//     res.setHeader('content-type', ' application/json');
//     res.setHeader('Access-Control-Allow-Origin', '*');
//     res.writeHead(200)//status code HTTP 200 / ok
//     let dataObj = {"id": 123, "name": "bob", "email": "bob@gmail.com"}
//     let data = JSON.stringify(dataObj)
//     res.end(data)
// });

// server.listen(1234, function(){
//     console.log('listening on port 1234');
// })

const express = require('express');
const cors = require('cors');

const app = express();
const port = 1234;

const prefix = "/api";

app.use(express.json());
app.use(cors());

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

module.exports.resetServerState = function () {
    //Does nothing
};

app.get(prefix  + '/notes', (req, res) => {
    return res.status(200).json(notes);
});



app.delete(prefix + '/notes/:noteId', (req, res) => {
    
    res.status(404).json({ 'message': "Note with id " + req.params.noteId + " does not exist." });
});

app.post(prefix + '/notes', (req, res) => {
    
    return res.status(201).json(myNote);
});
        

//Default: Not supported
app.use('*', (req, res) => {
    res.status(405).send('Operation not supported.');
});

app.listen(port, () => {
    console.log('Todo note app listening on port ' + port);
});