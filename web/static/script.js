let customRows = [];
let gTableRows = [];

const gModexIds = ['m1', 'm2', 'm3', 'm4'];
const gPilotIds = ['p1', 'p2', 'p3', 'p4'];
const gRioIds= ['r1', 'r2', 'r3', 'r4'];

function getModexes() {
    return gModexIds.map(id => document.getElementById(id).value);
}

function getPilots() {
    return gPilotIds.map(id => document.getElementById(id).value);
}

function getRios() {
    return gRioIds.map(id => document.getElementById(id).value);
}

async function fetchData() {
    try {
        const response = await fetch('/data')
        if (response.ok)
            return await response.json();
    } catch (error) {
        console.log("data fetch error: " + error);
    }
    return {};
}

function refreshData() {
    if (document.getElementById("use_empty_msndata").checked) {
        generateRows([]);
        renderTable();
        return;
    }

    fetchData()
        .then(data => {
            const rowData = data
                .filter(entry => entry.TAIL_NUMBER.trim() !== '')
                .filter(entry => getModexes().includes(entry.TAIL_NUMBER));
            generateRows(rowData);
            renderTable();
        })
        .catch(err => {
            console.error('Error loading JSON:', err);
        })
}

function updateRowsFromInputs() {
    gTableRows.forEach((row, idx) => {
        const pilotInput = document.getElementsByName(`plt_name_${idx}`)[0];
        const rioInput = document.getElementsByName(`rio_name_${idx}`)[0];
        const tailNumberInput = document.getElementsByName(`tail_number_${idx}`)[0];
        const weaponTypeInput = document.getElementsByName(`weapon_type_${idx}`)[0];
        const weaponInput = document.getElementsByName(`weapon_${idx}`)[0];
        const targetInput = document.getElementsByName(`target_${idx}`)[0];
        const targetAngelsInput = document.getElementsByName(`target_angels_${idx}`)[0];
        const angelsInput = document.getElementsByName(`angels_${idx}`)[0];
        const speedInput = document.getElementsByName(`speed_${idx}`)[0];
        const rangeInput = document.getElementsByName(`range_${idx}`)[0];
        const hitInput = document.getElementsByName(`hit_${idx}`)[0];
        const destroyedInput = document.getElementsByName(`destroyed_${idx}`)[0];

        row.plt_name = pilotInput ? pilotInput.value : "";
        row.rio_name = rioInput ? rioInput.value : "";
        row.tail_number = tailNumberInput ? tailNumberInput.value : "";
        row.weapon_type = weaponTypeInput ? weaponTypeInput.value : "";
        row.weapon = weaponInput ? weaponInput.value : "";
        row.target = targetInput ? targetInput.value : "";
        row.target_angels = targetAngelsInput ? parseFloat(targetAngelsInput.value) || "" : "";
        row.angels = angelsInput ? parseFloat(angelsInput.value) || "" : "";
        row.speed = speedInput ? parseFloat(speedInput.value) || "" : "";
        row.range = rangeInput ? parseFloat(rangeInput.value) || "" : "";
        row.hit = hitInput ? hitInput.checked : false;
        row.destroyed = destroyedInput ? destroyedInput.checked : false;
    });
}

function addCustomRow() {
    const emptyRow = {
        plt_name: "",
        tail_number: "",
        weapon_type: "A/A",
        weapon: "",
        target: "",
        target_angels: "",
        angels: "",
        speed: "",
        range: "",
        hit: false,
        destroyed: false,
        rio_name: ""
    };
    updateRowsFromInputs();

    gTableRows.push(emptyRow);
    renderTable();  // To render the new row immediately after adding it
}

function popCustomRow() {
    if (gTableRows.length > 0) {
        updateRowsFromInputs();
        gTableRows.pop();  // Remove the last custom row
        renderTable();  // Re-render the table after removing a row
    } else {
        alert("No rows to remove!");
    }
}

function generateRows(data) {
    const modexes = getModexes();
    const pilots = getPilots();
    const rios = getRios();

    let mappedData = [];

    mappedData = data
        .map(entry => {
            const index = modexes.indexOf(entry.TAIL_NUMBER);
            return {
                plt_name: pilots[index] || "",
                tail_number: entry.TAIL_NUMBER || "",
                weapon_type: entry.TYPE === 1 ? "A/A" : entry.TYPE === 0 ? "A/G" : "N/A",
                weapon: entry.WEAPON_NAME || "",
                target: entry.TGT_NAME || "",
                target_angels: entry.ANGELS_TGT > 0 || "",
                angels: entry.ANGELS > 0 || "",
                speed: entry.SPEED > 0 || "",
                range: entry.RANGE > 0 || "",
                hit: entry.HIT || false,
                destroyed: entry.DESTROYED || false,
                rio_name: rios[index] || ""
            };
        });

    const usedModexes = mappedData.map(entry => entry.tail_number);
    const unusedModexes = modexes.filter(modex => modex.trim() !== '' && !usedModexes.includes(modex));

    unusedModexes.forEach((modex, idx) => {
        mappedData.push({
            plt_name: pilots[modexes.indexOf(modex)] || "",
            tail_number: modex,
            weapon_type: "N/A",
            weapon: "",
            target: "",
            target_angels: "",
            angels: "",
            speed: "",
            range: "",
            hit: false,
            destroyed: false,
            rio_name: rios[modexes.indexOf(modex)] || ""
        });
    });

    gTableRows = mappedData.concat(customRows);
}

function renderTable() {
    const tableBody = document.getElementById('table-body');
    const rows = gTableRows;

    tableBody.innerHTML = '';
    rows.forEach((row, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="text" list="pilots" class="input_table" value="${row.plt_name}" name="plt_name_${idx}" required/></td>
            <td><input type="text" list="rios" class="input_table" value="${row.rio_name}" name="rio_name_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.tail_number}" name="tail_number_${idx}" required /></td>
            <td><input type="text" list="weapon_types" class="input_table" value="${row.weapon_type}" name="weapon_type_${idx}" required /></td>
            <td><input type="text" list="weapons" class="input_table" value="${row.weapon}" name="weapon_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.target}" name="target_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.target_angels}" name="target_angels_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.angels}" name="angels_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.speed}" name="speed_${idx}" /></td>
            <td><input type="text" class="input_table" value="${row.range}" name="range_${idx}" /></td>
            <td><input type="checkbox" class="input_table" ${row.hit ? 'checked' : ''} name="hit_${idx}" /></td>
            <td><input type="checkbox" class="input_table" ${row.destroyed ? 'checked' : ''} name="destroyed_${idx}" /></td>
        `;
        tableBody.appendChild(tr);
    });
}

function updateNames() {
    const modexes = getModexes();

    fetchData()
        .then(data => {
            if (document.getElementById("use_empty_msndata").checked) {
                refreshData();
                return;
            }

            const modexMap = data.reduce((map, entry) => {
                if (modexes.includes(entry.TAIL_NUMBER)) {
                    map[entry.TAIL_NUMBER] = {
                        pilot_name: entry.PILOT_NAME || "",
                        rio_name: entry.RIO_NAME || ""
                    };
                }
                return map;
            }, {});

            modexes.forEach((modex, index) => {
                if (modex.trim() !== '') {
                    const names = modexMap[modex] || { pilot_name: "", rio_name: "" };
                    document.getElementById(`p${index + 1}`).value = names.pilot_name;
                    document.getElementById(`r${index + 1}`).value = names.rio_name;
                } else {
                    // Clear values if Modex is empty
                    document.getElementById(`p${index + 1}`).value = "";
                    document.getElementById(`r${index + 1}`).value = "";
                }
            });
            refreshData();
        })
        .catch(error => {
            console.error('Error loading JSON:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('submit_form');
    form.addEventListener('submit', function(event) {
        const isConfirmed = confirm('Are you sure you want to upload the debrief?');
        if (!isConfirmed) {
            event.preventDefault();
        }
    });
});