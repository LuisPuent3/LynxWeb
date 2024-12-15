const express = require('express');
const authController = require('../controllers/authController');

const router = express.Router();

router.post('/register', authController.registerUser); // POST /api/auth/register
router.post('/login', authController.loginUser);       // POST /api/auth/login

module.exports = router;
