const express = require('express');
const router = express.Router();

const { getConnection } = require('../../connection');

const user = "utente";
const org = "org1";
router.post('/asset', async (req, res) => {
    // const transactionName = "SaveAltAsset2";
    const transactionName = "SaveAsset";
    const body = req.body;
    const key = `${body.design}.${body.player}.${body.printer}`;
    
    try {
        const conn = await getConnection(user, org); 
        conn.contract.submitTransaction(transactionName, key, body.gcode, body.snapshot, body.piece);
        res.status(201).json({"message": "asset saved"});
    } catch (error) {
        res.status(500).json({"message": `error saving asset: ${error}`});
    }

});

router.get('/asset', async (req, res) => {
    const transactionName = "GetAsset";
    let body = req.body;
    if (Object.keys(body).length == 0) {
        body = req.query;
    }
    const key = `${body.design}.${body.player}.${body.printer}`;
    try {
        const conn = await getConnection(user, org);
        const result = await conn.contract.evaluateTransaction(transactionName, key);
        res.json(JSON.parse(result.toString()));
    } catch (error) {
        res.status(500).json({"message": `error fetching asset: ${error}`})
    }
})

router.get('/average', async (req, res) => {
    const transactionName = "GetAverage";
    let body = req.body;
    if(Object.keys(body).length == 0) {
        body = req.query;
    }
    const key = `${body.design}.${body.player}.${body.printer}`;
    try {
        const conn = await getConnection(user, org);
        const result = await conn.contract.evaluateTransaction(transactionName, key);
        res.json(JSON.parse(result.toString()));
    } catch (error) {
        res.status(500).json({"message": `error fetching average: ${error}`})
    }
})


module.exports = router;