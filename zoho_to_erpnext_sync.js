const axios = require("axios");

// ============================================================
// CONFIG — fill in your real values here (or better, load from
// environment variables so secrets don't sit in the file)
// ============================================================
const CONFIG = {
  zoho: {
    clientId: "1000.M2S203CZ6SYB0XLVQ1GE6T0XQRICOH",
    clientSecret: "407b21f9f60c78070b5f1eb9f12345bff923eb0336",
    refreshToken: "1000.541a6c11b294d8f2ddb95a22f43f6f49.10480f70dfe991882c9268e126261d85",
    accountsBaseUrl: "https://accounts.zoho.com",
    peopleBaseUrl: "https://people.zoho.com",
  },
};

// Optional: pass a date as a command-line arg, e.g.
//   node print_zoho_attendance.js 15-07-2026
// Otherwise it defaults to "yesterday" based on this machine's clock.
function getTargetDate() {
  const argDate = process.argv[2];
  if (argDate) return argDate;

  const d = new Date();
  d.setDate(d.getDate() - 1);
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = d.getFullYear();
  return `${dd}-${mm}-${yyyy}`; // dd-MM-yyyy — match your Zoho People org date format
}

// Step 1: exchange refresh token for a fresh access token
async function getAccessToken() {
  const { clientId, clientSecret, refreshToken, accountsBaseUrl } = CONFIG.zoho;

  const response = await axios.post(`${accountsBaseUrl}/oauth/v2/token`, null, {
    params: {
      grant_type: "refresh_token",
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
    },
  });

  if (!response.data.access_token) {
    throw new Error(
      "Failed to get access token. Raw response: " + JSON.stringify(response.data)
    );
  }

  return response.data.access_token;
}

// Step 2: fetch the attendance report for a single date (all employees)
async function getAttendanceForDate(accessToken, date) {
  const { peopleBaseUrl } = CONFIG.zoho;

  const response = await axios.get(
    `${peopleBaseUrl}/people/api/attendance/getUserReport`,
    {
      params: { sdate: date, edate: date },
      headers: { Authorization: `Zoho-oauthtoken ${accessToken}` },
    }
  );

  return response.data;
}

// Main — just fetch and print, no writes anywhere
async function main() {
  const targetDate = getTargetDate();
  console.log(`Fetching attendance for date: ${targetDate}`);
  console.log("----------------------------------------");

  try {
    const accessToken = await getAccessToken();
    console.log("Access token acquired.");
    console.log("----------------------------------------");

    const report = await getAttendanceForDate(accessToken, targetDate);
    console.log(JSON.stringify(report, null, 2));
  } catch (err) {
    console.error("Error fetching attendance:");
    if (err.response) {
      console.error(JSON.stringify(err.response.data, null, 2));
    } else {
      console.error(err.message);
    }
  }
}

main();