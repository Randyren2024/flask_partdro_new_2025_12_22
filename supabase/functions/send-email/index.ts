import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import nodemailer from "npm:nodemailer@6.9.7";

const SMTP_HOSTNAME = Deno.env.get("SMTP_HOSTNAME") || "smtp.exmail.qq.com";
const SMTP_PORT = Number(Deno.env.get("SMTP_PORT") || 465);
const SMTP_USER = Deno.env.get("SMTP_USER") || "info@partdro.com";
const SMTP_PASSWORD = Deno.env.get("SMTP_PASSWORD");

const transporter = nodemailer.createTransport({
  host: SMTP_HOSTNAME,
  port: SMTP_PORT,
  secure: SMTP_PORT === 465, // true for 465, false for other ports
  auth: {
    user: SMTP_USER,
    pass: SMTP_PASSWORD,
  },
});

console.log("Email service started");

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: { 'Access-Control-Allow-Origin': '*' } })
  }

  try {
    const { record } = await req.json();

    if (!record) {
      return new Response("No record found in body", { status: 400 });
    }

    // Format the email body
    // Customize this based on your actual table columns
    const html = `
      <h2>New Partner Application Received</h2>
      <p><strong>Time:</strong> ${new Date().toLocaleString()}</p>
      <h3>Details:</h3>
      <table border="1" cellpadding="5" style="border-collapse: collapse;">
        ${Object.entries(record).map(([key, value]) => `
          <tr>
            <td><strong>${key}</strong></td>
            <td>${value}</td>
          </tr>
        `).join('')}
      </table>
    `;

    const info = await transporter.sendMail({
      from: `"Partdro System" <${SMTP_USER}>`,
      to: "info@partdro.com",
      subject: `New Partner Application: ${record.email || 'No Email'}`, // Assuming 'email' column exists
      html: html,
    });

    console.log("Message sent: %s", info.messageId);

    return new Response(JSON.stringify({ success: true, messageId: info.messageId }), {
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
    });
  } catch (error) {
    console.error("Error sending email:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
    });
  }
});
