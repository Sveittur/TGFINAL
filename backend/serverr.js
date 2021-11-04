const express = require('express');
const cors = require('cors');

const app = express();
const port = 3000;

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

app.get(prefix  + '/activeEnemies', (req, res) => {
    return res.status(200).json(notes);
});



app.delete(prefix  + '/activeEnemies/:enemyID', (req, res) => {

    res.status(404).json({ 'message': "Note with id " + req.params.noteId + " does not exist." });
});

app.post(prefix  + '/activeEnemies', (req, res) => {
    
    return res.status(201).json(myNote);
});
        

//Default: Not supported
app.use('*', (req, res) => {
    res.status(405).send('Operation not supported.');
});

app.listen(port, () => {
    console.log('Todo note app listening on port ' + port);
});