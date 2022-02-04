const express = require('express');
const path = require('path');

const app = express();
// body parser middleware
app.use(express.json());
// app.use(express.urlencoded({ extended: false}));

app.use('/api/', require('./routes/api/api'));

app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 12345;



app.listen(PORT, ()=> console.log(`server started on port ${PORT}`));