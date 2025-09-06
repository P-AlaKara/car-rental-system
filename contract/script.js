/* Data model and hydration */
const fields = {
  operatorName: '',
  operatorAddress: '',
  operatorContact: '',
  operatorEmail: '',
  renteeName: '',
  renteeAddress: '',
  renteeDob: '',
  renteeLicence: '',
  renteeState: '',
  vehicleRegistration: '',
  vehicleMake: '',
  vehicleModel: '',
  vehicleYear: '',
  vehicleVin: '',
  vehicleColor: '',
  fees: []
};

function hydrate(data) {
  const merged = { ...fields, ...data };
  for (const [key, value] of Object.entries(merged)) {
    if (key === 'fees') continue;
    const el = document.getElementById(key);
    if (el) {
      el.textContent = value || '\u00A0';
    }
  }
  // Inline renter name and date
  const nameInline = document.getElementById('renteeNameInline');
  if (nameInline) nameInline.textContent = merged.renteeName || '\u00A0';
  const dateSigned = document.getElementById('dateSigned');
  if (dateSigned) dateSigned.textContent = new Date().toLocaleString();

  // Fees table
  const feesBody = document.getElementById('feesBody');
  if (feesBody) {
    feesBody.innerHTML = '';
    (merged.fees || []).forEach(item => {
      const tr = document.createElement('tr');
      const tdDesc = document.createElement('td');
      tdDesc.textContent = item.description;
      const tdAmt = document.createElement('td');
      tdAmt.className = 'num';
      tdAmt.textContent = formatCurrency(item.amount);
      tr.appendChild(tdDesc);
      tr.appendChild(tdAmt);
      feesBody.appendChild(tr);
    });
  }
}

function formatCurrency(num) {
  if (num === undefined || num === null || num === '') return '';
  try {
    return new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD', maximumFractionDigits: 2 }).format(Number(num));
  } catch (e) { return String(num); }
}

/* Signature Pad */
let signaturePad, sigCanvasCtx;
function setupSignaturePad() {
  const canvas = document.getElementById('signaturePad');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  sigCanvasCtx = ctx;
  let drawing = false;
  let lastX = 0, lastY = 0;

  function startDraw(x, y) { drawing = true; lastX = x; lastY = y; }
  function drawLine(x, y) {
    if (!drawing) return;
    ctx.strokeStyle = '#111';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    lastX = x; lastY = y;
  }
  function endDraw() { drawing = false; }

  canvas.addEventListener('mousedown', e => startDraw(e.offsetX, e.offsetY));
  canvas.addEventListener('mousemove', e => drawLine(e.offsetX, e.offsetY));
  window.addEventListener('mouseup', endDraw);

  canvas.addEventListener('touchstart', e => {
    const t = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    startDraw(t.clientX - rect.left, t.clientY - rect.top);
    e.preventDefault();
  }, { passive: false });
  canvas.addEventListener('touchmove', e => {
    const t = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    drawLine(t.clientX - rect.left, t.clientY - rect.top);
    e.preventDefault();
  }, { passive: false });
  canvas.addEventListener('touchend', endDraw);

  document.getElementById('sig-clear')?.addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const img = document.getElementById('signatureImage');
    if (img) { img.style.display = 'none'; img.src = ''; }
  });

  document.getElementById('sig-apply')?.addEventListener('click', () => {
    const dataUrl = canvas.toDataURL('image/png');
    const img = document.getElementById('signatureImage');
    if (img) { img.src = dataUrl; img.style.display = 'block'; }
  });
}

/* Controls */
function setupControls() {
  document.getElementById('btn-print')?.addEventListener('click', () => {
    window.print();
  });
  document.getElementById('btn-clear')?.addEventListener('click', () => {
    hydrate({});
    const canvas = document.getElementById('signaturePad');
    if (sigCanvasCtx && canvas) sigCanvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    const img = document.getElementById('signatureImage');
    if (img) { img.style.display = 'none'; img.src = ''; }
  });
  document.getElementById('btn-load-example')?.addEventListener('click', () => {
    hydrate(exampleData());
  });
}

function exampleData() {
  return {
    operatorName: 'Aeron Rentals (ABN 69 627 445 332)',
    operatorAddress: '49 Lipton Drive, Thomastown VIC 3074',
    operatorContact: '0455 020 606',
    operatorEmail: 'aeronrentals766@gmail.com',
    renteeName: 'Wesley K Ngupa',
    renteeAddress: '2 / 11 Burrows Avenue, Doveton VIC 3175',
    renteeDob: '28 Dec 1986',
    renteeLicence: '062824448',
    renteeState: 'VIC',
    vehicleRegistration: '1ZZ8RP',
    vehicleMake: 'TOYOTA',
    vehicleModel: 'KLUGER',
    vehicleYear: '2013',
    vehicleVin: '5TDZK3EH65S123882',
    vehicleColor: 'WHITE',
    fees: [
      { description: '3.1 Standard Excess Fee Bronze', amount: 500.00 },
      { description: '3.2 Additional 1 – Age Excess if under 25 Years of age', amount: 1500.00 },
      { description: '3.3 Additional 2 – Unlisted Driver Excess', amount: 500.00 },
      { description: '3.4 Additional 3 – Age Excess if under 25 Years of age', amount: 1500.00 },
      { description: '3.5 Admin Fees', amount: 165.00 },
      { description: '3.6 Rego Recovery Fees Daily Charges', amount: 2.50 },
      { description: '3.7 Road Side Assistance Daily Charges', amount: 3.70 },
      { description: '3.8 Cleaning Fees', amount: 110.00 },
      { description: '3.9 Excess Reduction Daily Charges', amount: 41.00 }
    ]
  };
}

document.addEventListener('DOMContentLoaded', () => {
  setupSignaturePad();
  setupControls();
  hydrate({});
});

