const fs = require("fs");

let contacts;
let csv = "ticket_id,ticket_trace/contact\n";

const readDataFromFile = async () => {
  const data = await fs.readFileSync("contacts.json", "utf8");
  return data;
};
const SIZE = 500000;
let root = new Array(SIZE);
for (let i = 0; i < SIZE; i++) {
  root[i] = i;
}
const findRoot = (u) => {
  if (root[u] == u) return u;
  root[u] = findRoot(root[u]);
  return root[u];
};

const printRoot = () => {
  let ans = "";
  for (let i = 0; i < root.length; i++) {
    const a = findRoot(i);
    ans += a + " ";
  }
  console.log(ans);
};
const modifyData = async (data) => {
  let mpEmail = {};
  let mpPhone = {};
  let mpOrder = {};
  let mpContact = {};
  data.forEach((el, index) => {
    if (!mpEmail[el.Email]) mpEmail[el.Email] = [];
    mpEmail[el.Email].push(el.Id);

    if (!mpPhone[el.Phone]) mpPhone[el.Phone] = [];
    mpPhone[el.Phone].push(el.Id);

    if (!mpOrder[el.OrderId]) mpOrder[el.OrderId] = [];
    mpOrder[el.OrderId].push(el.Id);

    if (!mpContact[el.Od]) mpContact[el.Id] = 0;
    mpContact[el.Id] += el.Contacts;
    if (index % 10000 == 0) console.log("complete ", index);
  });

  const emails = Object.keys(mpEmail);
  const phones = Object.keys(mpPhone);
  const contacts = Object.keys(mpContact);
  const orders = Object.keys(mpOrder);

  emails.forEach((email) => {
    if (email == "") {
    } else {
      for (let i = 1; i < mpEmail[email].length; i++) {
        const a = mpEmail[email][i];
        const b = mpEmail[email][i - 1];

        const u = findRoot(a);
        const v = findRoot(b);
        root[u] = root[v];
      }
    }
  });

  phones.forEach((phone) => {
    if (phone == "") {
    } else {
      for (let i = 1; i < mpPhone[phone].length; i++) {
        const a = mpPhone[phone][i];
        const b = mpPhone[phone][i - 1];

        const u = findRoot(a);
        const v = findRoot(b);
        root[u] = root[v];
      }
    }
  });

  contacts.forEach((contact) => {
    if (contact == "") {
    } else {
      for (let i = 1; i < mpContact[contact].length; i++) {
        const a = mpContact[contact][i];
        const b = mpContact[contact][i - 1];

        const u = findRoot(a);
        const v = findRoot(b);

        root[u] = root[v];
      }
    }
  });

  orders.forEach((order) => {
    if (order == "") {
    } else {
      for (let i = 1; i < mpOrder[order].length; i++) {
        const a = mpOrder[order][i];
        const b = mpOrder[order][i - 1];

        const u = findRoot(a);
        const v = findRoot(b);
        root[u] = root[v];
      }
    }
  });

  console.log("root");
  printRoot();

  let answerContact = {};
  root.forEach((el, i) => {
    console.log(el);
    if (!answerContact[el]) answerContact[el] = { contact: 0, id: [] };
    answerContact[el].contact += data[i].Contacts;
    answerContact[el].id.push(data[i].Id);
  });
  let realAnswer = [];
  let keyArray = Object.keys(answerContact);
  for(let i of keyArray){
    for(let j of answerContact[i].id){
      realAnswer.push({id:j,data:answerContact[i].id.join('-')+', '+answerContact[i].contact})
    }
  }
  realAnswer.sort((a,b) => a.id - b.id)
  for(let i of realAnswer){
    csv += i.id+',\"'+i.data+'\"\n';
  }
  fs.writeFileSync('answer.csv',csv)
};

const main = async () => {
  contacts = await readDataFromFile();
  contacts = JSON.parse(contacts);
  await modifyData(contacts);
};
main();

