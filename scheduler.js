const express = require('express');
const router = express.Router();
const cron = require('node-cron');
const { EmailJSResponseStatus } = require('@emailjs/browser');
const emailjs = require('@emailjs/nodejs');

// Initialize EmailJS with your public and private keys
emailjs.init({
  publicKey: "lhfP3lB03VJ6CTZUJ",
  privateKey: "TMWMhgzB-roCv1_hj2PRK" // Get this from your EmailJS dashboard
});

router.post('/schedule-email', async (req, res) => {
  try {
    const { email, message, attachment_name, attachment_data, scheduledTime } = req.body;
    
    // Create a unique identifier for this email
    const emailId = `${email}_${Date.now()}`;
    const scheduledDateTime = new Date(scheduledTime);
    const minute = scheduledDateTime.getMinutes();
    const hour = scheduledDateTime.getHours();
    const day = scheduledDateTime.getDate();
    const month = scheduledDateTime.getMonth() + 1;
    
    console.log('Scheduling email for:', {
      email,
      scheduledTime: scheduledDateTime.toLocaleString(),
      hasAttachment: !!attachment_data
    });

    cron.schedule(`${minute} ${hour} ${day} ${month} *`, async () => {
      try {
        console.log('Processing scheduled email:', emailId);
        
        const templateParams = {
          to_email: email,
          message: message,
          attachment_name: attachment_name,
          attachment_data: attachment_data
        };

        const result = await emailjs.send(
          'service_270q8fl',
          'template_kpkkahu',
          templateParams,
          {
            publicKey: "lhfP3lB03VJ6CTZUJ",
            privateKey: "TMWMhgzB-roCv1_hj2PRK" // Same as above
          }
        );

        console.log('Scheduled email sent successfully:', result);
      } catch (error) {
        console.error('Error sending scheduled email:', error);
      }
    });
    
    res.json({ 
      message: `Email scheduled successfully for ${scheduledDateTime.toLocaleString()}`,
      emailId: emailId 
    });
  } catch (error) {
    console.error('Error scheduling email:', error);
    res.status(500).json({ error: 'Failed to schedule email' });
  }
});

module.exports = router;