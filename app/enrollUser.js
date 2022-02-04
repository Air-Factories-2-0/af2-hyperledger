const { Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const path = require('path');

const { buildCAClient, registerAndEnrollUser, buildCCP, buildWallet } = require('./utils');

const mspOrg1 = 'Org1MSP';
const mspOrg2 = 'Org2MSP';

const enrollToOrg1CA = async (UserID) => {
    console.log('\n--> Registering and enrolling new user');
    const ccpOrg1 = buildCCP('org1');
    const caOrg1Client = buildCAClient(FabricCAServices, ccpOrg1, 'ca.org1.example.com');

    const walletPathOrg1 = path.join(__dirname, 'wallet/org1');
    const walletOrg1 = await buildWallet(Wallets, walletPathOrg1);

    x509Identity = await registerAndEnrollUser(caOrg1Client, walletOrg1, mspOrg1, UserID, 'org1.department1');
    return x509Identity;
}


const enrollToOrg2CA = async (UserID) => {
    console.log('\n--> Registering and enrolling new user');
    const ccpOrg2 = buildCCP('org1');
    const caOrg2Client = buildCAClient(FabricCAServices, ccpOrg2, 'ca.org2.example.com');

    const walletPathOrg2 = path.join(__dirname, 'wallet/org2');
    const walletOrg2 = await buildWallet(Wallets, walletPathOrg2);

    x509Identity = await registerAndEnrollUser(caOrg2Client, walletOrg2, mspOrg2, UserID, 'org2.department1');
    return x509Identity;
}

const enrollFunctions = {
    'org1': enrollToOrg1CA,
    'org2': enrollToOrg2CA,
}

exports.enrollUser = async(userID, org) => {
   try {
        if (enrollFunctions[org] === undefined) {
            console.error(`no org ${org}`);
            process.exit(1);
        }
        return await enrollFunctions[org](userID);
   } catch (error) {
       console.error(`error in enrolling user ${error}`);
   }
}
