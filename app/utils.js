const fs = require('fs');
const path = require('path');

const adminUserId = "admin";
const adminUserPasswd = "adminpw";


exports.buildCCP = (org) => {
    const filepath = `./connection/connection-${org}.json`;
    const exists = fs.existsSync(filepath);

    if (!exists) {
        throw new Error (`no such file: ${filepath}`);
    }
    const contents = fs.readFileSync(filepath, 'utf-8');

    // build json object from file contents
    const ccp = JSON.parse(contents);

    console.log(`Loaded network configuration located at ${filepath}`);
    return ccp;
}


exports.buildWallet = async (Wallets, walletPath) => {
    // Creates new wallet for managing identity
    let wallet;

    if (walletPath) {
        wallet = await Wallets.newFileSystemWallet(walletPath);
    } else {
        try {
            wallet = await Wallets.newFileSystemWallet('./identity/user/utente/wallet');
            const credPath = path.join(dir, '/connection/org1/User1@org1.example.com/');
            const certificate = fs.readFileSync(path.join(credPath, '/msp/signcerts/User1@org1.example.com-cert.pem')).toString();
            const privateKey = fs.readFileSync(path.join(credPath, '/msp/keystore/priv_sk')).toString();

            const identityLabel = "utente";

            const identity = {
                credentials: {
                    certificate,
                    privateKey,
                },
                mspId: 'Org1MSP',
                type: 'X.509',
            };

            await wallet.put(identityLabel, identity);

        } catch (error) {
            console.log(`Error adding to wallet. ${error}`);
            console.log(error.stack);
        }
    }
    return wallet;
}

exports.buildCAClient = (FabricCAServices, ccp, caHostName) => {
    // Creates new CA client for interacting with CA.
    const caInfo = ccp.certificateAuthorities[caHostName];
    const caTLSCACerts = caInfo.tlsCACerts.pem;
    const caClient = new FabricCAServices(caInfo.url, { trustedRoots: caTLSCACerts, verify: false }, caInfo.caName);

    console.log(`Built a CA Client named ${caInfo.caName}`);
    return caClient;
}

exports.enrollAdmin = async (caClient, wallet, orgMspId) => {
    try {
        // check to see if we've already enrolled the admin user.
        const identity = await wallet.get(adminUserId);
        if (identity) {
            console.log("An identity for the admin user already exists in the wallet");
            return
        }

        // enroll the admin user, and import the new identity into the wallet
        const enrollment = await caClient.enroll({ enrollmentID: adminUserId, enrollmentSecret: adminUserPasswd});
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: orgMspId,
            type: 'X.509',
        };
        await wallet.put(adminUserId, x509Identity);
        console.log("Successfully enrolled admin user and imported it into the wallet");
    }
    catch(error) {
        console.error(`Failed to enroll admin user : ${error}`);
    }
}

exports.registerUser = async (caClient, wallet, orgMspId, userId, affiliation) => {
    const adminIdentity = await wallet.get(adminUserId);
    if (!adminIdentity) {
        console.log('An identity for the admin user does not exist in the wallet');
        console.log('Enroll the admin user before retrying');
        return;
    }
    // build a user object for authenticating with the CA
    const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
    const adminUser = await provider.getUserContext(adminIdentity, adminUserId);

    // register the user and returns the enrollment secret
    const secret = await caClient.register({
        affiliation: affiliation,
        enrollmentID: userId,
        role: 'client',
    }, adminUser);

    return secret;
}

exports.enrollUser = async (caClient, enrollmentID, enrollmentSecret) => {
    const enrollment = await caClient.enroll({
        enrollmentID: enrollmentID,
        enrollmentSecret: enrollmentSecret,
    });

    return enrollment;
}

exports.registerAndEnrollUser = async (caClient, wallet, orgMspId, userId, affiliation) => {
    try {
        // check to see if we've already enrolled the user
        const userIdentity = await wallet.get(userId);
        if (userIdentity) {
            console.log(`An identity for the user ${userId} already exists in the wallet`);
            return;
        }

        // must use an admin to register a new user
        const adminIdentity = await wallet.get(adminUserId);
        if (!adminIdentity) {
            console.log('An identity for the admin user does not exist in the wallet');
            console.log('Enroll the admin user before retrying');
            return;
        }

        // build a user object for authenticating with the CA
        const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
        const adminUser = await provider.getUserContext(adminIdentity, adminUserId);

        // register the user, enroll the user, and import the new identity into the wallet.
        // if affiliation is specified by client, the affiliation value must be configured in CA
        const secret = await caClient.register({
            affiliation: affiliation,
            enrollmentID: userId,
            role: 'client',
        }, adminUser);

        const enrollment = await caClient.enroll({
            enrollmentID: userId,
            enrollmentSecret: secret,
            // csr: csr,
        });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: orgMspId,
            type: "X.509",
        };
        // await wallet.put(userId, x509Identity);
        return x509Identity;
        // console.log(`Successfully registered and enrolled user ${userId} and imported it into the wallet`);
    }
    catch(error) {
        console.error(`Failed to register user : ${error}`);
    }
}