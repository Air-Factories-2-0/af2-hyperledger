const { Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');

const path = require('path');
const { buildCAClient, buildCCP, buildWallet, enrollAdmin } = require('./utils');

const mspOrg1 = 'Org1MSP';
const mspOrg2 = 'Org2MSP';

const enrollToOrg1CA = async () => {
    console.log('\n--> Enrolling the Org1 CA admin');
    // const ccpOrg1 = buildCCP('./connection/connection-org1.json');
    const ccpOrg1 = buildCCP("org1");
    const caOrg1Client = buildCAClient(FabricCAServices, ccpOrg1, 'ca.org1.example.com');

    const walletPathOrg1 = path.join(__dirname, 'wallet/org1');
    const walletOrg1 = await buildWallet(Wallets, walletPathOrg1);

    await enrollAdmin(caOrg1Client, walletOrg1, mspOrg1);
}


const enrollToOrg2CA = async () => {
    console.log('\n--> Enrolling the Org2 CA admin');
    // const ccpOrg2 = buildCCP('./connection/connection-org2.json');
    const ccpOrg2 = buildCCP("org2");
    const caOrg2Client = buildCAClient(FabricCAServices, ccpOrg2, 'ca.org2.example.com');

    const walletPathOrg2 = path.join(__dirname, 'wallet/org2');
    const walletOrg2 = await buildWallet(Wallets, walletPathOrg2);

    await enrollAdmin(caOrg2Client, walletOrg2, mspOrg2);
}

async function enrollAdmins() {
    await enrollToOrg1CA();
    await enrollToOrg2CA();
}

module.exports = enrollAdmins;

enrollAdmins();

