const express = require('express');
const axios = require('axios');

const app = express();
const port = 8001;

const operators_api = {
    '+': 'sum',
    '-': 'subtract',
    '*': 'multiply',
    '/': 'divide'
}

async function calc(operand1, operand2, operator) {
    console.log("Request:", operand1, operator, operand2);

    try {
        const res = await axios.get(`http://127.0.0.1:8000/${operators_api[operator]}/${operand1}/${operand2}`);
        console.log("Response:", res.data);
        return res.data;
    } catch (error) {
        console.log(error);
        return "bad request";
    }
}

app.get('/', async (req, res) => {
  if (
    (req.query.operand1 !== undefined) && 
    (req.query.operand2 !== undefined) && 
    (req.query.operator) !== undefined) {
        const resp = await calc(req.query.operand1, req.query.operand2, req.query.operator)
        res.send(resp.toString());
  } else {
    res.sendFile(`${__dirname}/static/index.html`);
  }
  
})

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
})
