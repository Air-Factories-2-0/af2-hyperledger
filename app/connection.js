const { Gateway, Wallets } = require("fabric-network");

const { buildCCP} = require('./utils');
const { enrollUser } = require('./enrollUser');
const chaincodeName = "chaincode";
const channelName = "mychannel";

let connection;

const setConnection = async(user, path) => {
    const ccp = buildCCP(user.org);
    const wallet = await Wallets.newFileSystemWallet(path);
    let id = await wallet.get(user.name)
    // se l'utente non esiste nel wallet viene fatto l'enrollment
    if (!id) {
        id = await enrollUser(user.name, user.org);
        await wallet.put(user.name, id);
    }

    const gateway = new Gateway();
    try {
        await gateway.connect(ccp, {
            wallet: wallet,
            identity: user.name,
            discovery: { enabled: true, asLocalhost: true } // using asLocalhost as this gateway is using a fabric network deployed locally
        });

        const network = await gateway.getNetwork(channelName);

        const contract = network.getContract(chaincodeName);

        connection = {
            gateway: gateway,
            contract: contract,
        }
        return connection;
    } catch (e) {
        console.error(e);
    }
}

exports.getConnection = async (userID, org) => {
    if (!connection){
        const user = {
            name: userID,
            org: org,
        }
        connection = await setConnection(user, "./wallet/");
    }
    return connection;
}