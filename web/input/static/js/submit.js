const AppState = {
    pilotCounter: 1,
    agWeaponCount: { 1: 0 },
    uploadedImages: {},
    aaRowCounter: 0,
    selectedCallsign: null,
    jsonData: null
};

// ===== Constants =====
const MAX_PILOTS = 4;
const MODEX_MIN = 100;
const MODEX_MAX = 999;
const MISSION_NUMBER_MIN = 1000;
const MISSION_NUMBER_MAX = 9999;

// ===== Utility Functions =====
function createElement(tag, className, innerHTML = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
}

function removeElement(selector) {
    const element = document.querySelector(selector);
    if (element) element.remove();
}

// ===== A/A Weapons Functions =====
function addAARow() {
    AppState.aaRowCounter++;
    const tbody = document.getElementById('aa-table-body');

    const newRow = createElement('tr');
    newRow.setAttribute('data-aa-row-id', AppState.aaRowCounter);
    newRow.innerHTML = `
                <td>
                    <input type="text" pattern="\\d{3}" required class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][modex]">
                </td>

                <td>
                    <input type="text" required list="aa-weapons" class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][weapon]">
                </td>

                <td>
                    <input type="text" required class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][target]">
                </td>

                <td>
                    <input type="number" min="0" max="99" class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][range]">
                </td>

                <td>
                    <input type="number" min="0.1" max="3" step="0.01" class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][speed]">
                </td>

                <td>
                    <input type="number" min="0" max="50" class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][own_altitude]">
                </td>

                <td>
                    <input type="number" min="0" max="50" class="field-value-aircrew" 
                        style="border: none; 
                        background: transparent; 
                        text-align: center;" 
                        name="aa_weapons[${AppState.aaRowCounter}][target_altitude]">
                </td>

                <td style="text-align: center;">
                    <input type="checkbox" style="transform: scale(1.2);" 
                        name="aa_weapons[${AppState.aaRowCounter}][hit]" value="1">
                </td>

                <td style="border: none; background: transparent; padding-left: 10px; width: 30px; text-align: center;">
                    <button type="button" class="aa-remove-btn" onclick="removeAARow(${AppState.aaRowCounter})">✕</button>
                </td>
            `;

    tbody.appendChild(newRow);
}

function removeAARow(rowId) {
    removeElement(`[data-aa-row-id="${rowId}"]`);
}

// ===== A/G Weapons Functions =====
function addWeaponCard(pilotId) {
    if (!AppState.agWeaponCount[pilotId]) {
        AppState.agWeaponCount[pilotId] = 0;
    }

    const weaponId = ++AppState.agWeaponCount[pilotId];
    const agVertical = document.getElementById(`ag-vertical-${pilotId}`);
    const addButton = agVertical.querySelector('.btn-add');

    const newWeaponCard = createElement('div', 'weapon-card');
    newWeaponCard.setAttribute('data-weapon-id', weaponId);
    newWeaponCard.setAttribute('data-pilot-id', pilotId);
    newWeaponCard.innerHTML = `
        <button type="button" class="btn-remove" onclick="removeWeaponCard(${pilotId}, ${weaponId})">✕</button>
        <div class="weapon-name">
            <input type="text" required minlength="3" maxlength="32"
                   class="field-value-aircrew" style="text-align: left; padding: 0px 8px;"
                   placeholder="Weapon Name*"
                   name="ag_weapons[${pilotId}][${weaponId}][weapon_name]">
        </div>

        <div class="target-dmpi-table">
            <select class="field-value" style="color-scheme: dark"
                    name="ag_weapons[${pilotId}][${weaponId}][target_type]"
                    onchange="updateTargetInput(${pilotId}, ${weaponId})">
                <option value="none" selected>NONE</option>
                <option value="dmpi">DMPI ID</option>
                <option value="target">TARGET</option>
            </select>

            <div class="weapon-name">
                <input type="text" minlength="3" maxlength="64"
                       class="field-value-aircrew" style="text-align: left; padding: 0px 8px;"
                       name="ag_weapons[${pilotId}][${weaponId}][target_value]"
                       id="target-input-${pilotId}-${weaponId}"
                       placeholder="" disabled>
            </div>
        </div>

        <input type="hidden" name="ag_weapons[${pilotId}][${weaponId}][image_data]" 
            id="image-data-${pilotId}-${weaponId}">
        <input type="hidden" name="ag_weapons[${pilotId}][${weaponId}][bda_result]" 
            id="bda-result-hidden-${pilotId}-${weaponId}">
    `;

    agVertical.insertBefore(newWeaponCard, addButton);
}

function removeWeaponCard(pilotId, weaponId) {
    const weaponCard = document.querySelector(`[data-weapon-id="${weaponId}"][data-pilot-id="${pilotId}"]`);
    if (weaponCard) {
        weaponCard.remove();

        const uploadId = `upload-${pilotId}-${weaponId}`;
        delete AppState.uploadedImages[uploadId];

        updateBDACards();
    }
}

function updateTargetInput(pilotId, weaponId) {
    const select = document.querySelector(`select[name="ag_weapons[${pilotId}][${weaponId}][target_type]"]`);
    const input = document.getElementById(`target-input-${pilotId}-${weaponId}`);

    switch(select.value) {
        case 'none':
            input.placeholder = '';
            input.disabled = true;
            input.value = '';
            break;
        case 'dmpi':
            input.placeholder = 'DMPI ID';
            input.disabled = false;
            break;
        case 'target':
            input.placeholder = 'TARGET';
            input.disabled = false;
            break;
    }

    updateBDACards();
}

// ===== Pilot Card Functions =====
function addPilotCard() {
    AppState.pilotCounter++;
    const pilotGrid = document.getElementById('aircrew');

    if (AppState.pilotCounter >= MAX_PILOTS) {
        AppState.pilotCounter = MAX_PILOTS;
        pilotGrid.querySelectorAll('.btn-add').forEach(btn => btn.remove());
    }

    pilotGrid.querySelectorAll('.btn-remove').forEach(btn => btn.remove());

    const newCard = createElement('div', 'pilot-card');
    newCard.setAttribute('data-pilot-id', AppState.pilotCounter);
    newCard.innerHTML = `
                <button type="button" class="btn-remove" onclick="removePilotCard(${AppState.pilotCounter})">✕</button>
                ${AppState.jsonData ? `<button type="button" class="btn-load-modex" onclick="loadDataByModex(${AppState.pilotCounter})" title="Load weapons from server">↓</button>` : ''}
                <div class="callsign-name">${AppState.selectedCallsign || 'CALLSIGN'}${AppState.pilotCounter}</div>
                <div class="pilot-details">
                    <div>
                        <div class="field-label" style="text-align: center; padding-left: 0px;">MODEX*</div>
                        <input type="text" required pattern="\\d{3}"
                               class="field-value-aircrew"
                               name="aircrew[${AppState.pilotCounter}][modex]"
                               id="aircrew_${AppState.pilotCounter}_modex">
                    </div>
                    <div>
                        <div class="field-label" style="text-align: center; padding-left: 0px;">AIRCREW</div>
                        <div style="display: flex;">
                            <input type="text" required minlength="2" maxlength="32"
                                   class="field-value-aircrew"
                                   name="aircrew[${AppState.pilotCounter}][pilot]"
                                   placeholder="Pilot*"
                                   id="aircrew_${AppState.pilotCounter}_pilot">
                            <input type="text" minlength="2" maxlength="32"
                                   class="field-value-aircrew"
                                   name="aircrew[${AppState.pilotCounter}][rio]"
                                   placeholder="Rio"
                                   id="aircrew_${AppState.pilotCounter}_rio">
                        </div>
                    </div>
                </div>
            `;

    AppState.agWeaponCount[AppState.pilotCounter] = 0;

    const newAGCard = createElement('div', 'ag-grid-vertical-box');
    newAGCard.setAttribute('data-ag-pilot-id', AppState.pilotCounter);
    newAGCard.innerHTML = `
                <div class="ag-grid-vertical" id="ag-vertical-${AppState.pilotCounter}">
                    <div class="ag-grid-header">${AppState.selectedCallsign || 'CALLSIGN'}${AppState.pilotCounter}</div>
                    <button type="button" class="btn-add" onclick="addWeaponCard(${AppState.pilotCounter})" style="height: 120px;">
                        <span class="add-icon">+</span>
                    </button>
                </div>
            `;

    const lastButton = pilotGrid.querySelector('.btn-add:last-child');
    pilotGrid.insertBefore(newCard, lastButton);

    document.getElementById('ag-grid').insertBefore(newAGCard, document.getElementById('ag-grid').lastChild);
}

function removePilotCard(pilotId) {
    const modexInput = document.getElementById(`aircrew_${pilotId}_modex`);
    const modexValue = modexInput ? modexInput.value : null;

    removeElement(`[data-pilot-id="${pilotId}"]`);
    removeElement(`[data-ag-pilot-id="${pilotId}"]`);

    if (modexValue) {
        const aaRows = document.querySelectorAll('#aa-table-body tr');
        aaRows.forEach(row => {
            const modexCell = row.querySelector('input[name*="[modex]"]');
            if (modexCell && modexCell.value === modexValue) {
                row.remove();
            }
        });
    }

    delete AppState.agWeaponCount[pilotId];
    AppState.pilotCounter--;

    const remainingPilots = document.querySelectorAll('.pilot-card');

    if (remainingPilots.length > 1) {
        let highestId = 1;
        let mostRecentPilot = null;

        remainingPilots.forEach(pilot => {
            const id = parseInt(pilot.getAttribute('data-pilot-id'));
            if (id > highestId) {
                highestId = id;
                mostRecentPilot = pilot;
            }
        });

        if (mostRecentPilot && highestId > 1) {
            const removeBtn = createElement('button', 'btn-remove');
            removeBtn.type = 'button';
            removeBtn.onclick = () => removePilotCard(highestId);
            removeBtn.innerHTML = '✕';
            mostRecentPilot.appendChild(removeBtn);
        }
    }

    if (remainingPilots.length < MAX_PILOTS) {
        const pilotGrid = document.getElementById('aircrew');
        const existingAddButtons = pilotGrid.querySelectorAll('.btn-add');

        if (existingAddButtons.length === 0) {
            const addButton1 = createElement('button', 'btn-add');
            addButton1.type = 'button';
            addButton1.onclick = addPilotCard;
            addButton1.innerHTML = '<span class="add-icon">+</span>';

            const addButton2 = createElement('button', 'btn-add');
            addButton2.type = 'button';
            addButton2.onclick = addPilotCard;
            addButton2.innerHTML = '<span class="add-icon">+</span>';

            pilotGrid.insertBefore(addButton1, pilotGrid.firstChild);
            pilotGrid.appendChild(addButton2);
        }
    }

    // Clean up uploaded images
    Object.keys(AppState.uploadedImages).forEach(uploadId => {
        if (uploadId.includes(`-${pilotId}-`)) {
            delete AppState.uploadedImages[uploadId];
        }
    });

    updateBDACards();
}

// ===== BDA Functions =====
function updateBDACards() {
    const bdaGrid = document.getElementById('bda-grid');

    // Store current BDA results
    const currentBDAResults = {};
    const existingSelects = bdaGrid.querySelectorAll('select[name*="bda_result"]');
    existingSelects.forEach(select => {
        const match = select.name.match(/ag_weapons\[(\d+)\]\[(\d+)\]\[bda_result\]/);
        if (match) {
            const pilotId = match[1];
            const weaponId = match[2];
            currentBDAResults[`${pilotId}-${weaponId}`] = select.value;
        }
    });

    bdaGrid.innerHTML = '';

    const weaponCards = document.querySelectorAll('.weapon-card');

    weaponCards.forEach(weaponCard => {
        const pilotId = weaponCard.getAttribute('data-pilot-id');
        const weaponId = weaponCard.getAttribute('data-weapon-id');

        const weaponNameInput = weaponCard.querySelector(
            `input[name="ag_weapons[${pilotId}][${weaponId}][weapon_name]"]`
        );
        const targetSelect = weaponCard.querySelector(
            `select[name="ag_weapons[${pilotId}][${weaponId}][target_type]"]`
        );
        const targetInput = document.getElementById(`target-input-${pilotId}-${weaponId}`);

        if (targetSelect && targetSelect.value !== 'none' && targetInput && targetInput.value.trim() !== '') {
            const callsign = document.querySelector(`[data-pilot-id="${pilotId}"] .callsign-name`).textContent;
            const weaponName = weaponNameInput ? weaponNameInput.value : '';
            const targetType = targetSelect.value === 'dmpi' ? 'DMPI ID' : 'TARGET';
            const targetValue = targetInput.value;
            const uploadId = `upload-${pilotId}-${weaponId}`;
            const bdaKey = `${pilotId}-${weaponId}`;
            const savedBDAResult = currentBDAResults[bdaKey] || '';

            const bdaCard = createBDACard({
                callsign,
                targetType,
                targetValue,
                weaponName,
                uploadId,
                pilotId,
                weaponId,
                savedBDAResult
            });

            bdaGrid.appendChild(bdaCard);

            // Update hidden input
            const hiddenInput = document.getElementById(`bda-result-hidden-${pilotId}-${weaponId}`);
            if (hiddenInput && savedBDAResult) {
                hiddenInput.value = savedBDAResult;
            }

            // Restore uploaded image if exists
            if (AppState.uploadedImages[uploadId]) {
                setTimeout(() => {
                    const uploadArea = document.getElementById(uploadId);
                    if (uploadArea) {
                        displayUploadedImage(uploadArea, uploadId, pilotId, weaponId, AppState.uploadedImages[uploadId]);
                    }
                }, 0);
            }
        }
    });
}

function createBDACard(params) {
    const bdaCard = createElement('div', 'bda-card');
    bdaCard.innerHTML = `
                <div class="aircraft-callsign">${params.callsign}</div>
                <div class="target-name">${params.targetType}: ${params.targetValue}</div>
                <div class="weapon-name">${params.weaponName}</div>
                <div class="file-upload-area" id="${params.uploadId}"
                    ondrop="handleDrop(event, '${params.uploadId}', ${params.pilotId}, ${params.weaponId})"
                    ondragover="handleDragOver(event)"
                    ondragleave="handleDragLeave(event)">
                    <div class="file-upload-controls">
                        <div>Drop image here</div>
                        <button type="button" class="file-upload-button"
                                onclick="event.stopPropagation(); document.getElementById('file-input-${params.uploadId}').click()">
                            Browse Files
                        </button>
                        <button type="button" class="file-upload-button"
                                onclick="event.stopPropagation(); pasteFromClipboard('${params.uploadId}', ${params.pilotId}, ${params.weaponId})">
                            Paste from Clipboard
                        </button>
                    </div>
                    <input type="file" id="file-input-${params.uploadId}" class="hidden-file-input"
                        accept="image/*" onchange="handleFileSelect(event, '${params.uploadId}', ${params.pilotId}, ${params.weaponId})">
                </div>
                <select class="field-value" style="width: 100%; margin-top: 10px; background: var(--bg-section);"
                        name="ag_weapons[${params.pilotId}][${params.weaponId}][bda_result]"
                        id="bda-result-${params.pilotId}-${params.weaponId}">
                    <option value="">Select BDA Result...</option>
                    <option value="1 - Direct Hit Visual" ${params.savedBDAResult === '1 - Direct Hit Visual' ? 'selected' : ''}>1 - Direct Hit Visual</option>
                    <option value="2 - Direct Hit Sensor" ${params.savedBDAResult === '2 - Direct Hit Sensor' ? 'selected' : ''}>2 - Direct Hit Sensor</option>
                    <option value="3 - Damaged Visual" ${params.savedBDAResult === '3 - Damaged Visual' ? 'selected' : ''}>3 - Damaged Visual</option>
                    <option value="4 - Damaged Sensor" ${params.savedBDAResult === '4 - Damaged Sensor' ? 'selected' : ''}>4 - Damaged Sensor</option>
                    <option value="5 - Near Miss/Unknown Damage" ${params.savedBDAResult === '5 - Near Miss/Unknown Damage' ? 'selected' : ''}>5 - Near Miss/Unknown Damage</option>
                    <option value="6 - Missed Target" ${params.savedBDAResult === '6 - Missed Target' ? 'selected' : ''}>6 - Missed Target</option>
                    <option value="7 - No Drop/Abort" ${params.savedBDAResult === '7 - No Drop/Abort' ? 'selected' : ''}>7 - No Drop/Abort</option>
                </select>
            `;
    return bdaCard;
}

// ===== Image Upload Functions =====
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e, uploadId, pilotId, weaponId) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) {
        try {
            validateFileSize(files[0]);
            displayImage(files[0], uploadId, pilotId, weaponId);
        } catch (error) {
            alert(`❌ Upload failed: ${error.message}`);
        }
    }
}

function handleFileSelect(e, uploadId, pilotId, weaponId) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        try {
            validateFileSize(file);
            displayImage(file, uploadId, pilotId, weaponId);
        } catch (error) {
            alert(`❌ Upload failed: ${error.message}`);
            // Clear the file input so user can try again
            e.target.value = '';
        }
    }
}

async function displayImage(file, uploadId, pilotId, weaponId) {
    const reader = new FileReader();
    reader.onload = async function(e) {
        const imageData = e.target.result;

        try {
            const fileType = file.type.split('/')[1].toLowerCase();

            if (!(['jpeg', 'jpg', 'png', 'gif'].includes(fileType))) {
                throw new Error(`Unsupported file type (Supported file types: jpg, jpeg, png, gif)`);
            }

            AppState.uploadedImages[uploadId] = imageData;

            // Store image data in hidden input
            const hiddenInput = document.getElementById(`image-data-${pilotId}-${weaponId}`);
            if (hiddenInput) {
                hiddenInput.value = imageData;
            }

            const uploadArea = document.getElementById(uploadId);
            if (uploadArea) {
                displayUploadedImage(uploadArea, uploadId, pilotId, weaponId, imageData);
            }

        } catch (error) {
            alert(`❌ Image processing failed: ${error.message}`);

            // Clear any partial data
            delete AppState.uploadedImages[uploadId];
            const hiddenInput = document.getElementById(`image-data-${pilotId}-${weaponId}`);
            if (hiddenInput) {
                hiddenInput.value = '';
            }
        }
    };

    reader.onerror = function() {
        alert('❌ Failed to read the image file. Please try again.');
    };

    reader.readAsDataURL(file);
}

function displayUploadedImage(uploadArea, uploadId, pilotId, weaponId, imageData) {
    uploadArea.innerHTML = `
                <img src="${imageData}" alt="Target Image">
                <div class="image-overlay-controls">
                    <button type="button" class="overlay-button"
                            onclick="event.stopPropagation(); document.getElementById('file-input-${uploadId}').click()">
                        Change
                    </button>
                    <button type="button" class="overlay-button danger"
                            onclick="event.stopPropagation(); removeImage('${uploadId}', ${pilotId}, ${weaponId})">
                        Remove
                    </button>
                </div>
                <input type="file" id="file-input-${uploadId}" class="hidden-file-input"
                    accept="image/*" onchange="handleFileSelect(event, '${uploadId}', ${pilotId}, ${weaponId})">
            `;
}

function removeImage(uploadId, pilotId, weaponId) {
    delete AppState.uploadedImages[uploadId];

    // Clear hidden input
    const hiddenInput = document.getElementById(`image-data-${pilotId}-${weaponId}`);
    if (hiddenInput) {
        hiddenInput.value = '';
    }

    const uploadArea = document.getElementById(uploadId);
    if (uploadArea) {
        uploadArea.innerHTML = `
                    <div class="file-upload-controls">
                        <div>Drop image here</div>
                        <button type="button" class="file-upload-button"
                                onclick="event.stopPropagation(); document.getElementById('file-input-${uploadId}').click()">
                            Browse Files
                        </button>
                        <button type="button" class="file-upload-button"
                                onclick="event.stopPropagation(); pasteFromClipboard('${uploadId}', ${pilotId}, ${weaponId})">
                            Paste from Clipboard
                        </button>
                    </div>
                    <input type="file" id="file-input-${uploadId}" class="hidden-file-input"
                        accept="image/*" onchange="handleFileSelect(event, '${uploadId}', ${pilotId}, ${weaponId})">
                `;
    }
}

async function pasteFromClipboard(uploadId, pilotId, weaponId) {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (const clipboardItem of clipboardItems) {
            for (const type of clipboardItem.types) {
                if (type.startsWith('image/')) {
                    const blob = await clipboardItem.getType(type);

                    // Validate clipboard image size
                    try {
                        validateFileSize(blob);
                        displayImage(blob, uploadId, pilotId, weaponId);
                        return;
                    } catch (error) {
                        alert(`❌ Clipboard image too large: ${error.message}`);
                        return;
                    }
                }
            }
        }
        alert('No image found in clipboard');
    } catch (err) {
        console.error('Failed to read clipboard contents: ', err);
        alert('Failed to access clipboard. Please use drag & drop or file selection.');
    }
}
// ===== Callsign Functions =====
function updateAllCallsigns(callsign) {
    // Update pilot card callsigns
    document.querySelectorAll('.callsign-name').forEach((element, index) => {
        element.textContent = `${callsign}${index + 1}`;
    });

    // Update AG grid headers
    document.querySelectorAll('.ag-grid-header').forEach((element, index) => {
        element.textContent = `${callsign}${index + 1}`;
    });

    AppState.selectedCallsign = callsign;
    document.getElementById('callsign').value = callsign;
}

// ===== Form Data Management =====
function setNestedValue(obj, path, value) {
    // Handle array notation like aircrew[1][modex]
    const arrayMatch = path.match(/^(\w+)\[(\d+)\]\[(\w+)\]$/);
    if (arrayMatch) {
        const [, arrayName, index, fieldName] = arrayMatch;

        if (!obj[arrayName]) obj[arrayName] = {};
        if (!obj[arrayName][index]) obj[arrayName][index] = {};

        obj[arrayName][index][fieldName] = value;
        return;
    }

    // Handle nested array notation like ag_weapons[1][2][weapon_name]
    const nestedArrayMatch = path.match(/^(\w+)\[(\d+)\]\[(\d+)\]\[(\w+)\]$/);
    if (nestedArrayMatch) {
        const [, arrayName, pilotId, weaponId, fieldName] = nestedArrayMatch;

        if (!obj[arrayName]) obj[arrayName] = {};
        if (!obj[arrayName][pilotId]) obj[arrayName][pilotId] = {};
        if (!obj[arrayName][pilotId][weaponId]) obj[arrayName][pilotId][weaponId] = {};

        obj[arrayName][pilotId][weaponId][fieldName] = value;
        return;
    }

    // Handle simple field names
    obj[path] = value;
}

function getFormDataAsJSON() {
    const formData = new FormData(document.getElementById('apStrikeForm'));
    const data = {};

    for (let [name, value] of formData.entries()) {
        setNestedValue(data, name, value);
    }

    return data;
}

function getCompleteFormData() {
    const baseData = getFormDataAsJSON();

    // Convert aircrew object to array
    if (baseData.aircrew) {
        baseData.aircrew = Object.values(baseData.aircrew).map(pilot => ({
            modex: pilot.modex || '',
            pilot: pilot.pilot || '',
            rio: pilot.rio || ''
        }));
    }

    // Convert AA weapons object to array
    if (baseData.aa_weapons) {
        baseData.aa_weapons = Object.values(baseData.aa_weapons).map(weapon => ({
            modex: weapon.modex || '',
            weapon: weapon.weapon || '',
            target: weapon.target || '',
            range: weapon.range ? parseFloat(weapon.range) : null,
            speed: weapon.speed ? parseFloat(weapon.speed) : null,
            own_altitude: weapon.own_altitude ? parseFloat(weapon.own_altitude) : null,
            target_altitude: weapon.target_altitude ? parseFloat(weapon.target_altitude) : null,
            hit: weapon.hit === '1'
        }));
    }

    // Convert AG weapons object to array
    if (baseData.ag_weapons) {
        const agWeaponsArray = [];
        Object.keys(baseData.ag_weapons).forEach(pilotId => {
            Object.keys(baseData.ag_weapons[pilotId]).forEach(weaponId => {
                const weapon = baseData.ag_weapons[pilotId][weaponId];
                if (weapon.weapon_name || weapon.target_value) {
                    agWeaponsArray.push({
                        pilot_id: parseInt(pilotId),
                        weapon_id: parseInt(weaponId),
                        weapon_name: weapon.weapon_name || '',
                        target_type: weapon.target_type || 'none',
                        target_value: weapon.target_value || '',
                        image_data: weapon.image_data || '',
                        bda_result: weapon.bda_result || ''
                    });
                }
            });
        });
        baseData.ag_weapons = agWeaponsArray;
    }

    // Add metadata
    baseData.form_metadata = {
        submission_time: new Date().toISOString(),
        total_aircrew: baseData.aircrew ? baseData.aircrew.length : 0,
        total_ag_weapons: baseData.ag_weapons ? baseData.ag_weapons.length : 0,
        total_aa_weapons: baseData.aa_weapons ? baseData.aa_weapons.length : 0,
        total_bdas: baseData.ag_weapons ? baseData.ag_weapons.filter(w => w.bda_result && w.bda_result.trim() !== '' && w.target_value && w.target_value.trim() !== '').length : 0,
        has_images: baseData.ag_weapons ? baseData.ag_weapons.some(w => w.image_data) : false
    };

    // Initialize empty arrays if not present
    if (!baseData.aircrew) baseData.aircrew = [];
    if (!baseData.aa_weapons) baseData.aa_weapons = [];
    if (!baseData.ag_weapons) baseData.ag_weapons = [];

    return baseData;
}

async function submitToBackend(formData) {
    const submitButton = document.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    // Move urlParams outside try block so it's accessible in catch
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('id');
    const isEditMode = editId && !isNaN(parseInt(editId)) && parseInt(editId) >= 1;

    try {
        submitButton.textContent = 'Submitting...';
        submitButton.disabled = true;

        let endpoint;
        if (isEditMode) {
            endpoint = `/edit-report/${editId}`;
            submitButton.textContent = 'Updating...';
        } else {
            endpoint = '/submit-report';
        }

        console.log(`Submitting to: ${endpoint} (POST)`);

        const compressedFormData = await compressFormData(formData);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(compressedFormData)
        });

        if (response.ok) {
            const result = await response.json();

            if (isEditMode) {
                submitButton.textContent = 'Updated Successfully!';
                setTimeout(() => {
                    window.location.href = `/debrief/${editId}`;
                }, 1000);
            } else {
                if (result.id) {
                    submitButton.textContent = 'Success! Redirecting...';
                    setTimeout(() => {
                        window.location.href = `/debrief/${result.id}`;
                    }, 1000);
                } else {
                    console.log('Server response:', result);
                }
            }
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Submission error:', error);
        const action = isEditMode ? 'update' : 'submit'; // Use isEditMode instead of urlParams
        alert(`❌ Failed to ${action} strike report:\n${error.message}`);

        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

async function compressFormData(formData) {
    const compressed = { ...formData };

    if (compressed.ag_weapons && compressed.ag_weapons.length > 0) {
        compressed.ag_weapons = await Promise.all(
            compressed.ag_weapons.map(async (weapon) => {
                if (weapon.image_data && weapon.image_data.length > 0) {
                    try {
                        const compressedImage = await compressImage(weapon.image_data);
                        return { ...weapon, image_data: compressedImage };
                    } catch (error) {
                        console.warn('Failed to compress image, using original:', error);
                        return weapon;
                    }
                }
                return weapon;
            })
        );
    }

    return compressed;
}

function compressImage(base64Image, maxWidth = 1024, quality = 0.8) {
    return new Promise((resolve, reject) => {
        // Extract the original format from the base64 string
        const formatMatch = base64Image.match(/^data:image\/([^;]+);base64,/);
        if (!formatMatch) {
            reject(new Error('Invalid base64 image format'));
            return;
        }

        const originalFormat = formatMatch[1].toLowerCase();

        if (originalFormat === 'gif') {
            const sizeInBytes = (base64Image.length * 3) / 4;
            const sizeInMB = sizeInBytes / (1024 * 1024);

            if (sizeInMB > 5) { // If larger than 5MB
                reject(new Error(`${originalFormat.toUpperCase()} file too large (${sizeInMB.toFixed(1)}MB). Please use a smaller file.`));
                return;
            }

            resolve(base64Image);
            return;
        }

        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // Calculate new dimensions while maintaining aspect ratio
            let { width, height } = img;
            const needsResize = width > maxWidth || height > maxWidth;

            if (needsResize) {
                if (width > height) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                } else {
                    width = (width * maxWidth) / height;
                    height = maxWidth;
                }
            }

            canvas.width = width;
            canvas.height = height;

            // For PNG images with transparency, preserve transparency
            if (originalFormat === 'png') {
                ctx.clearRect(0, 0, width, height);
            } else {
                // For JPEG, fill with white background
                ctx.fillStyle = '#FFFFFF';
                ctx.fillRect(0, 0, width, height);
            }

            // Draw the image
            ctx.drawImage(img, 0, 0, width, height);

            try {
                let outputFormat = 'image/jpeg';
                let outputQuality = quality;

                // Preserve PNG format for images with transparency
                if (originalFormat === 'png') {
                    outputFormat = 'image/png';
                    outputQuality = undefined; // PNG doesn't use quality parameter
                }

                const compressedBase64 = canvas.toDataURL(outputFormat, outputQuality);

                if (!needsResize && (base64Image.length * 3 / 4 / (1024*1024)) < 1) {
                    resolve(base64Image);
                } else {
                    resolve(compressedBase64);
                }
            } catch (error) {
                reject(error);
            }
        };

        img.onerror = () => reject(new Error('Failed to load image for compression'));
        img.src = base64Image;
    });
}

function updateSubmitButtonText() {
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('id');
    const isEditMode = editId && !isNaN(parseInt(editId)) && parseInt(editId) >= 1;

    const submitButton = document.getElementById('SubmitButton');
    if (submitButton && isEditMode) {
        submitButton.textContent = 'Update Debrief';
    }
}


// ===== JSON Data Loading Functions =====
function callsignToDL(callsign) {
    const match = callsign.match(/^([A-Z]+)(\d+)$/);
    if (!match) return null;

    const [, base, number] = match;
    const firstLetter = base.charAt(0);
    const lastLetter = base.charAt(base.length - 1);

    return `${firstLetter}${lastLetter}${number}`;
}

function filterDataByCallsign(jsonData, currentCallsign) {
    if (!currentCallsign || !jsonData) return [];

    const currentDL = callsignToDL(currentCallsign);
    if (!currentDL) return [];

    return jsonData.filter(entry => {
        if (!entry.DL_CALLSIGN) return false;
        const entryBase = entry.DL_CALLSIGN.replace(/\d$/, '');
        return entryBase === currentDL;
    });
}

function loadDataFromJSON(jsonData) {
    if (!jsonData || jsonData.length === 0) {
        return;
    }

    const currentCallsign = AppState.selectedCallsign;
    if (!currentCallsign) {
        alert('Please select a callsign first');
        return;
    }

    const filteredData = filterDataByCallsign(jsonData, currentCallsign);

    if (filteredData.length === 0) {
        alert(`No data found for ${currentCallsign}1`);
        return;
    }

    // Group data by aircraft
    const aircraftGroups = {};
    filteredData.forEach(entry => {
        if (!aircraftGroups[entry.DL_CALLSIGN]) {
            aircraftGroups[entry.DL_CALLSIGN] = [];
        }
        aircraftGroups[entry.DL_CALLSIGN].push(entry);
    });

    // Clear existing data
    const existingCards = document.querySelectorAll('.pilot-card[data-pilot-id]');
    existingCards.forEach((card, index) => {
        if (index > 0) {
            const pilotId = card.getAttribute('data-pilot-id');
            removePilotCard(parseInt(pilotId));
        }
    });

    document.getElementById('aa-table-body').innerHTML = '';
    AppState.aaRowCounter = 0;

    // Find the highest pilot number needed
    let maxPilotNumber = 1;
    Object.keys(aircraftGroups).forEach(dlCallsign => {
        const pilotNumber = parseInt(dlCallsign.slice(-1)); // Get last digit
        maxPilotNumber = Math.max(maxPilotNumber, pilotNumber);
    });

    // Create pilot cards up to the highest number needed
    for (let i = 2; i <= maxPilotNumber; i++) {
        addPilotCard();
    }

    // Process each aircraft and map to correct pilot card
    Object.keys(aircraftGroups).forEach(dlCallsign => {
        const aircraftData = aircraftGroups[dlCallsign];
        const firstEntry = aircraftData[0];

        // Extract pilot number from DL_CALLSIGN (last digit)
        const pilotNumber = parseInt(dlCallsign.slice(-1));

        // Fill aircrew data for the specific pilot card
        const modexInput = document.getElementById(`aircrew_${pilotNumber}_modex`);
        const pilotInput = document.getElementById(`aircrew_${pilotNumber}_pilot`);
        const rioInput = document.getElementById(`aircrew_${pilotNumber}_rio`);

        if (modexInput) modexInput.value = firstEntry.TAIL_NUMBER ?? '';
        if (pilotInput) pilotInput.value = firstEntry.PILOT_NAME ?? '';
        if (rioInput) rioInput.value = firstEntry.RIO_NAME ?? '';

        // Process weapons for this specific pilot
        aircraftData.forEach(entry => {
            if (entry.TYPE === 0) {
                // A/G Weapon
                addWeaponCard(pilotNumber);
                const weaponId = AppState.agWeaponCount[pilotNumber];

                const weaponNameInput = document.querySelector(`input[name="ag_weapons[${pilotNumber}][${weaponId}][weapon_name]"]`);
                const targetSelect = document.querySelector(`select[name="ag_weapons[${pilotNumber}][${weaponId}][target_type]"]`);
                const targetInput = document.getElementById(`target-input-${pilotNumber}-${weaponId}`);

                if (weaponNameInput) weaponNameInput.value = entry.WEAPON_NAME ?? '';
                if (entry.TGT_NAME === "NONE")
                    entry.TGT_NAME = ''
                if (entry.TGT_TNAME === "NONE")
                    entry.TGT_TNAME = ''

                if (targetSelect && (entry.TGT_NAME || entry.TGT_TNAME)) {
                    targetSelect.value = 'target';
                    targetSelect.dispatchEvent(new Event('change'));
                }
                if (targetInput) targetInput.value = entry.TGT_NAME ?? entry.TGT_TNAME ?? '';

            } else if (entry.TYPE === 1) {
                // A/A Weapon
                addAARow();

                const modexInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][modex]"]`);
                const weaponInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][weapon]"]`);
                const targetInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target]"]`);
                const rangeInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][range]"]`);
                const speedInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][speed]"]`);
                const ownAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][own_altitude]"]`);
                const targetAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target_altitude]"]`);
                const hitCheckbox = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][hit]"]`);

                if (modexInput) modexInput.value = entry.TAIL_NUMBER ?? '';
                if (weaponInput) weaponInput.value = entry.WEAPON_NAME ?? '';
                if (targetInput) targetInput.value = entry.TGT_TNAME ?? entry.TGT_NAME ?? '';
                if (rangeInput) rangeInput.value = entry.RANGE ?? '';
                if (speedInput) speedInput.value = entry.SPEED ?? '';
                if (ownAltInput) ownAltInput.value = entry.ANGELS ?? '';
                if (targetAltInput) targetAltInput.value = entry.ANGELS_TGT ?? '';
                if (hitCheckbox) hitCheckbox.checked = (entry.HIT === true || entry.DESTROYED === true);
            }
        });
    });

    // Mark loaded pilot cards
    for (let i = 1; i <= maxPilotNumber; i++) {
        const pilotCard = document.querySelector(`[data-pilot-id="${i}"]`);
        if (pilotCard) {
            // Check if this pilot card has any data
            const modexInput = document.getElementById(`aircrew_${i}_modex`);
            const pilotInput = document.getElementById(`aircrew_${i}_pilot`);

            // Only mark as loaded if it has modex or pilot name
            if ((modexInput && modexInput.value) || (pilotInput && pilotInput.value)) {
                pilotCard.setAttribute('data-loaded-from-json', 'true');
            }
        }
    }

    setTimeout(() => {
        updateBDACards();
    }, 100);
}


function handleJSONFileUpload() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.style.display = 'none';

    input.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const jsonData = JSON.parse(e.target.result);
                    loadDataFromJSON(jsonData);
                } catch (error) {
                    alert('Error parsing JSON file: ' + error.message);
                }
            };
            reader.readAsText(file);
        }
    };

    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

// ===== Event Listeners =====
function initializeEventListeners() {
    // Close popup
    document.getElementById('closePopupBtn').addEventListener('click', function() {
        document.getElementById('callsignPopup').style.display = 'none';
    });

    // Form submission
    document.getElementById('apStrikeForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = getCompleteFormData();
        submitToBackend(formData);
    });

    // Update BDA cards on input changes
    document.addEventListener('input', function(e) {
        if (e.target.name && (e.target.name.includes('weapon_name') || e.target.name.includes('target_value'))) {
            updateBDACards();
        }
    });

    // Handle BDA result changes
    document.addEventListener('change', function(e) {
        if (e.target.name && e.target.name.includes('bda_result')) {
            const match = e.target.name.match(/ag_weapons\[(\d+)\]\[(\d+)\]\[bda_result\]/);
            if (match) {
                const pilotId = match[1];
                const weaponId = match[2];
                const hiddenInput = document.getElementById(`bda-result-hidden-${pilotId}-${weaponId}`);
                if (hiddenInput) {
                    hiddenInput.value = e.target.value;
                }
            }
        }
    });

    // File upload area clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('file-upload-area') && !e.target.querySelector('img')) {
            const uploadId = e.target.id;
            if (uploadId) {
                document.getElementById(`file-input-${uploadId}`).click();
            }
        }
    });

}

// ===== Initialization =====
window.onload = function() {
    // Set current date
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const formattedDate = `${yyyy}-${mm}-${dd}`;
    document.getElementById("mission_date").value = formattedDate;

    // Setup callsign selection
    const callsignSelect = document.getElementById('callsignSelect');
    const confirmButton = document.getElementById('confirmCallsign');
    const popup = document.getElementById('callsignPopup');

    const loadButton = document.getElementById('loadButton');
    const manualButton = document.getElementById('manualButton');
    const missionDataSelect = document.getElementById('missionDataSelect');

    fetchMissionDataLabels();

    function updateButtonStates() {
        const hasCallsign = !!callsignSelect.value;
        const hasMissionData = !!missionDataSelect.value;

        loadButton.disabled = !hasCallsign || !hasMissionData;
        manualButton.disabled = !hasCallsign;
    }

    callsignSelect.addEventListener('change', updateButtonStates);
    missionDataSelect.addEventListener('change', updateButtonStates);

    loadButton.addEventListener('click', async function() {
        const selectedCallsign = callsignSelect.value;
        const selectedMissionId = missionDataSelect.value;

        if (selectedCallsign && selectedMissionId) {
            clearFormData();
            updateAllCallsigns(selectedCallsign);

            // Fetch and load the mission data
            const missionData = await fetchMissionData(selectedMissionId);
            AppState.jsonData = missionData;

            const firstCardLoadBtn = document.querySelector('[data-pilot-id="1"] .btn-load-modex');
            if (firstCardLoadBtn && missionData) {
                firstCardLoadBtn.style.display = '';
            }

            if (missionData) {
                loadDataFromJSON(missionData);
            }

            popup.style.display = 'none';
        }
    });

    // Manual button - only sets callsign
    manualButton.addEventListener('click', async function() {
        const selectedCallsign = callsignSelect.value;
        const selectedMissionId = missionDataSelect.value;

        if (selectedCallsign && selectedMissionId) {
            clearFormData()
            updateAllCallsigns(selectedCallsign);

            AppState.jsonData = await fetchMissionData(selectedMissionId);

            const firstCardLoadBtn = document.querySelector('[data-pilot-id="1"] .btn-load-modex');
            if (firstCardLoadBtn) {
                firstCardLoadBtn.style.display = ''; // Show the button explicitly
            }

            popup.style.display = 'none';
        }
    });

    // Initialize event listeners
    initializeEventListeners();
};

async function fetchMissionDataLabels() {
    try {
        const response = await fetch('/data-labels');
        const labels = await response.json();

        const missionDataSelect = document.getElementById('missionDataSelect');

        Object.entries(labels).forEach(([id, filename]) => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = filename;
            missionDataSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to fetch mission data labels:', error);
    }
}

function loadDataByModex(pilotId) {
    if (!AppState.jsonData) return;

    const card = document.querySelector(`[data-pilot-id="${pilotId}"]`);
    if (card && card.getAttribute('data-loaded-from-json') === 'true') {
        return;
    }

    const modexInput = document.getElementById(`aircrew_${pilotId}_modex`);
    const modexValue = modexInput ? modexInput.value : null;

    if (!modexValue) {
        alert('Please enter a modex first');
        return;
    }

    // Find all entries matching this modex
    const matchingEntries = AppState.jsonData.filter(entry =>
        entry.TAIL_NUMBER === modexValue
    );

    if (matchingEntries.length === 0) {
        alert(`No data found for modex ${modexValue}`);
        return;
    }

    // Load pilot data
    const firstEntry = matchingEntries[0];
    const pilotInput = document.getElementById(`aircrew_${pilotId}_pilot`);
    const rioInput = document.getElementById(`aircrew_${pilotId}_rio`);

    if (pilotInput && firstEntry.PILOT_NAME) pilotInput.value = firstEntry.PILOT_NAME;
    if (rioInput && firstEntry.RIO_NAME) rioInput.value = firstEntry.RIO_NAME;

    // Process weapons for this pilot
    matchingEntries.forEach(entry => {
        if (entry.TYPE === 0) {
            // A/G Weapon
            addWeaponCard(pilotId);
            const weaponId = AppState.agWeaponCount[pilotId];

            const weaponNameInput = document.querySelector(`input[name="ag_weapons[${pilotId}][${weaponId}][weapon_name]"]`);
            const targetSelect = document.querySelector(`select[name="ag_weapons[${pilotId}][${weaponId}][target_type]"]`);
            const targetInput = document.getElementById(`target-input-${pilotId}-${weaponId}`);

            if (weaponNameInput) weaponNameInput.value = entry.WEAPON_NAME ?? '';

            // Clean up target data - set to empty string if "NONE"
            if (entry.TGT_NAME === "NONE") entry.TGT_NAME = '';
            if (entry.TGT_TNAME === "NONE") entry.TGT_TNAME = '';

            // Only set target type to 'target' if there's actually target data
            if (targetSelect && (entry.TGT_NAME || entry.TGT_TNAME)) {
                targetSelect.value = 'target';
                targetSelect.dispatchEvent(new Event('change'));
                if (targetInput) targetInput.value = entry.TGT_NAME ?? entry.TGT_TNAME ?? '';
            } else {
                // Keep default 'none' selection if no target data
                if (targetSelect) {
                    targetSelect.value = 'none';
                    targetSelect.dispatchEvent(new Event('change'));
                }
            }

        } else if (entry.TYPE === 1) {
            // A/A Weapon
            addAARow();

            const modexInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][modex]"]`);
            const weaponInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][weapon]"]`);
            const targetInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target]"]`);
            const rangeInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][range]"]`);
            const speedInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][speed]"]`);
            const ownAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][own_altitude]"]`);
            const targetAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target_altitude]"]`);
            const hitCheckbox = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][hit]"]`);

            if (modexInput) modexInput.value = entry.TAIL_NUMBER ?? '';
            if (weaponInput) weaponInput.value = entry.WEAPON_NAME ?? '';
            if (targetInput) targetInput.value = entry.TGT_TNAME ?? entry.TGT_NAME ?? '';
            if (rangeInput) rangeInput.value = entry.RANGE ?? '';
            if (speedInput) speedInput.value = entry.SPEED ?? '';
            if (ownAltInput) ownAltInput.value = entry.ANGELS ?? '';
            if (targetAltInput) targetAltInput.value = entry.ANGELS_TGT ?? '';
            if (hitCheckbox) hitCheckbox.checked = entry.HIT === true;
        }
    });

    // Mark this pilot card as loaded
    const pilotCard = document.querySelector(`[data-pilot-id="${pilotId}"]`);
    if (pilotCard) {
        pilotCard.setAttribute('data-loaded-from-json', 'true');
        // Hide the load button after loading
        const loadBtn = pilotCard.querySelector('.btn-load-modex');
        if (loadBtn) loadBtn.style.display = 'none';
    }

    setTimeout(() => {
        updateBDACards();
    }, 100);
}

async function fetchMissionData(id) {
    try {
        const response = await fetch(`/data?id=${id}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch mission data:', error);
        return null;
    }
}
// Function to load complete form data from submit-data.json object
function loadFromSubmitDataJSON(submitDataJSON) {
    try {
        if (!submitDataJSON) {
            throw new Error('No submit data provided');
        }

        // If it's a string, parse it as JSON
        let submitData;
        if (typeof submitDataJSON === 'string') {
            submitData = JSON.parse(submitDataJSON);
        } else {
            submitData = submitDataJSON;
        }

        loadSubmitData(submitData);
        console.log('Submit data loaded successfully from provided JSON');
        return submitData;

    } catch (error) {
        console.error('Error loading submit data:', error);
        alert('Error loading submit data: ' + error.message);
        throw error;
    }
}

// Alternative function to load from file input (if still needed)
async function loadFromSubmitDataFile() {
    try {
        // Create file input for JSON selection
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.style.display = 'none';

        return new Promise((resolve, reject) => {
            input.onchange = async function(event) {
                const file = event.target.files[0];
                if (!file) {
                    reject(new Error('No file selected'));
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        const submitData = JSON.parse(e.target.result);
                        loadSubmitData(submitData);
                        resolve(submitData);
                    } catch (error) {
                        reject(new Error('Error parsing JSON file: ' + error.message));
                    }
                };
                reader.readAsText(file);
            };

            document.body.appendChild(input);
            input.click();
            document.body.removeChild(input);
        });

    } catch (error) {
        console.error('Error loading submit data:', error);
        alert('Error loading submit data: ' + error.message);
    }
}

// Main function to populate the form with submit data
function loadSubmitData(submitData) {
    try {
        // Hide popup if visible and fill required popup fields
        const popup = document.getElementById('callsignPopup');
        if (popup) {
            // Fill popup fields based on submit data
            const callsignSelect = document.getElementById('callsignSelect');
            if (callsignSelect && submitData.callsign) {
                callsignSelect.value = submitData.callsign;
            }

            // Hide the popup
            popup.style.display = 'none';
        }

        // Update callsign throughout the form
        if (submitData.callsign) {
            updateAllCallsigns(submitData.callsign);
        }

        // Clear existing form data
        clearFormData();

        // Load basic mission data
        loadBasicMissionData(submitData);

        // Load aircrew data
        if (submitData.aircrew && submitData.aircrew.length > 0) {
            loadAircrewData(submitData.aircrew);
        }

        // Load A/A weapons data
        if (submitData.aa_weapons && submitData.aa_weapons.length > 0) {
            loadAAWeaponsData(submitData.aa_weapons);
        }

        // Load A/G weapons data
        if (submitData.ag_weapons && submitData.ag_weapons.length > 0) {
            loadAGWeaponsData(submitData.ag_weapons);
        }

        // Load other form fields
        loadOtherFormData(submitData);

        // Update BDA cards after loading A/G weapons
        setTimeout(() => {
            updateBDACards();
            restoreBDAResults(submitData.ag_weapons);
            restoreUploadedImages(submitData.ag_weapons);
        }, 200);

        console.log('Submit data loaded successfully');

    } catch (error) {
        console.error('Error loading submit data:', error);
        alert('Error loading submit data: ' + error.message);
    }
}

function clearFormData() {
    const existingCards = document.querySelectorAll('.pilot-card[data-pilot-id]');
    existingCards.forEach((card, index) => {
        if (index > 0) {
            const pilotId = parseInt(card.getAttribute('data-pilot-id'));
            removePilotCard(pilotId);
        }
    });

    // Clear the first pilot card's data
    const firstModexInput = document.getElementById('aircrew_1_modex');
    const firstPilotInput = document.getElementById('aircrew_1_pilot');
    const firstRioInput = document.getElementById('aircrew_1_rio');

    if (firstModexInput) firstModexInput.value = '';
    if (firstPilotInput) firstPilotInput.value = '';
    if (firstRioInput) firstRioInput.value = '';

    // Remove the loaded-from-json attribute from first card
    const firstCard = document.querySelector('[data-pilot-id="1"]');
    if (firstCard) {
        firstCard.removeAttribute('data-loaded-from-json');
    }

    document.querySelectorAll('.weapon-card').forEach(weaponCard => {
        weaponCard.remove();
    });

    const bdaGrid = document.getElementById('bda-grid');
    if (bdaGrid) {
        bdaGrid.innerHTML = '';
    }

    document.getElementById('aa-table-body').innerHTML = '';
    AppState.aaRowCounter = 0;

    const allPilotCards = document.querySelectorAll('.pilot-card[data-pilot-id]');
    allPilotCards.forEach(card => {
        const pilotId = parseInt(card.getAttribute('data-pilot-id'));
        AppState.agWeaponCount[pilotId] = 0;
    });

    AppState.uploadedImages = {};

    AppState.pilotCounter = 1;
}

// Load basic mission information
function loadBasicMissionData(submitData) {
    const fieldMappings = {
        'mission_name': submitData.mission_name,
        'mission_number': submitData.mission_number,
        'mission_event': submitData.mission_event,
        'mission_date': submitData.mission_date,
        'opposition_type_number': submitData.opposition_type_number,
        'opposition_location': submitData.opposition_location,
        'engagement_result': submitData.engagement_result,
        'blue_casualties': submitData.blue_casualties,
        'mission_notes': submitData.mission_notes,
        'restrike_recommendation': submitData.restrike_recommendation,
        'callsign': submitData.callsign
    };

    Object.entries(fieldMappings).forEach(([fieldId, value]) => {
        const element = document.getElementById(fieldId);
        if (element && value !== undefined && value !== null) {
            element.value = value;
        }
    });
}

// Load aircrew data
function loadAircrewData(aircrewArray) {
    aircrewArray.forEach((aircrew, index) => {
        const pilotId = index + 1;

        // Add pilot card if needed
        while (pilotId > document.querySelectorAll('.pilot-card').length) {
            addPilotCard();
        }

        // Fill aircrew data
        const modexInput = document.getElementById(`aircrew_${pilotId}_modex`);
        const pilotInput = document.getElementById(`aircrew_${pilotId}_pilot`);
        const rioInput = document.getElementById(`aircrew_${pilotId}_rio`);

        if (modexInput && aircrew.modex) modexInput.value = aircrew.modex;
        if (pilotInput && aircrew.pilot) pilotInput.value = aircrew.pilot;
        if (rioInput && aircrew.rio) rioInput.value = aircrew.rio;
    });
}

// Load A/A weapons data
function loadAAWeaponsData(aaWeaponsArray) {
    aaWeaponsArray.forEach(weapon => {
        addAARow();

        const modexInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][modex]"]`);
        const weaponInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][weapon]"]`);
        const targetInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target]"]`);
        const rangeInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][range]"]`);
        const speedInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][speed]"]`);
        const ownAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][own_altitude]"]`);
        const targetAltInput = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][target_altitude]"]`);
        const hitCheckbox = document.querySelector(`input[name="aa_weapons[${AppState.aaRowCounter}][hit]"]`);

        if (modexInput && weapon.modex) modexInput.value = weapon.modex;
        if (weaponInput && weapon.weapon) weaponInput.value = weapon.weapon;
        if (targetInput && weapon.target) targetInput.value = weapon.target;
        if (rangeInput && weapon.range !== null && weapon.range !== undefined) rangeInput.value = weapon.range;
        if (speedInput && weapon.speed !== null && weapon.speed !== undefined) speedInput.value = weapon.speed;
        if (ownAltInput && weapon.own_altitude !== null && weapon.own_altitude !== undefined) ownAltInput.value = weapon.own_altitude;
        if (targetAltInput && weapon.target_altitude !== null && weapon.target_altitude !== undefined) targetAltInput.value = weapon.target_altitude;
        if (hitCheckbox) hitCheckbox.checked = weapon.hit === true;
    });
}

// Load A/G weapons data
function loadAGWeaponsData(agWeaponsArray) {
    // Group weapons by pilot_id
    const weaponsByPilot = {};
    agWeaponsArray.forEach(weapon => {
        const pilotId = weapon.pilot_id || 1;
        if (!weaponsByPilot[pilotId]) {
            weaponsByPilot[pilotId] = [];
        }
        weaponsByPilot[pilotId].push(weapon);
    });

    // Load weapons for each pilot
    Object.entries(weaponsByPilot).forEach(([pilotId, weapons]) => {
        const pilotIdInt = parseInt(pilotId);

        weapons.forEach(weapon => {
            addWeaponCard(pilotIdInt);
            const weaponId = AppState.agWeaponCount[pilotIdInt];

            // Fill weapon data
            const weaponNameInput = document.querySelector(`input[name="ag_weapons[${pilotIdInt}][${weaponId}][weapon_name]"]`);
            const targetSelect = document.querySelector(`select[name="ag_weapons[${pilotIdInt}][${weaponId}][target_type]"]`);
            const targetInput = document.getElementById(`target-input-${pilotIdInt}-${weaponId}`);
            const imageDataInput = document.getElementById(`image-data-${pilotIdInt}-${weaponId}`);

            if (weaponNameInput && weapon.weapon_name) {
                weaponNameInput.value = weapon.weapon_name;
            }

            if (targetSelect && weapon.target_type) {
                targetSelect.value = weapon.target_type;
                targetSelect.dispatchEvent(new Event('change'));
            }

            if (targetInput && weapon.target_value) {
                targetInput.value = weapon.target_value;
            }

            if (imageDataInput && weapon.image_data) {
                imageDataInput.value = weapon.image_data;
            }

            // Store image data for later restoration
            if (weapon.image_data) {
                const uploadId = `upload-${pilotIdInt}-${weaponId}`;
                AppState.uploadedImages[uploadId] = weapon.image_data;
            }
            if (weapon.image_path) {
                // Store the image path for later use
                weapon.stored_image_path = weapon.image_path;
            }
        });
    });
}

// Load other form data
function loadOtherFormData(submitData) {
    // Additional fields that might be in the submit data
    const additionalFields = [
        'opposition_type_number',
        'opposition_location',
        'engagement_result',
        'blue_casualties',
        'mission_notes',
        'restrike_recommendation'
    ];

    additionalFields.forEach(fieldName => {
        const element = document.getElementById(fieldName);
        if (element && submitData[fieldName] !== undefined && submitData[fieldName] !== null) {
            element.value = submitData[fieldName];
        }
    });
}

// Restore BDA results after BDA cards are created
function restoreBDAResults(agWeaponsArray) {
    if (!agWeaponsArray) return;

    agWeaponsArray.forEach(weapon => {
        const pilotId = weapon.pilot_id || 1;
        const weaponId = weapon.weapon_id || 1;

        if (weapon.bda_result) {
            const bdaSelect = document.getElementById(`bda-result-${pilotId}-${weaponId}`);
            const bdaHidden = document.getElementById(`bda-result-hidden-${pilotId}-${weaponId}`);

            if (bdaSelect) {
                bdaSelect.value = weapon.bda_result;
            }
            if (bdaHidden) {
                bdaHidden.value = weapon.bda_result;
            }
        }
    });
}

// Restore uploaded images after BDA cards are created
// Replace the existing restoreUploadedImages function with:
async function restoreUploadedImages(agWeaponsArray) {
    if (!agWeaponsArray) return;

    const urlParams = new URLSearchParams(window.location.search);
    const debriefId = urlParams.get('id');

    if (!debriefId) return;

    for (const weapon of agWeaponsArray) {
        const pilotId = weapon.pilot_id || 1;
        const weaponId = weapon.weapon_id || 1;

        if (weapon.image_path) {
            const uploadId = `upload-${pilotId}-${weaponId}`;
            const uploadArea = document.getElementById(uploadId);

            if (uploadArea) {
                try {
                    // Fetch the image from the server
                    const imageUrl = `/bda/${debriefId}/${weapon.image_path}`;
                    const response = await fetch(imageUrl);

                    if (response.ok) {
                        const blob = await response.blob();
                        const reader = new FileReader();

                        reader.onload = function(e) {
                            const imageData = e.target.result;

                            // Store in AppState
                            AppState.uploadedImages[uploadId] = imageData;

                            // Update the hidden input
                            const hiddenInput = document.getElementById(`image-data-${pilotId}-${weaponId}`);
                            if (hiddenInput) {
                                hiddenInput.value = imageData;
                            }

                            // Display the image
                            displayUploadedImage(uploadArea, uploadId, pilotId, weaponId, imageData);
                        };

                        reader.readAsDataURL(blob);
                    }
                } catch (error) {
                    console.error(`Failed to load image for weapon ${pilotId}-${weaponId}:`, error);
                }
            }
        } else if (weapon.image_data) {
            // Fallback to embedded image data if available
            const uploadId = `upload-${pilotId}-${weaponId}`;
            const uploadArea = document.getElementById(uploadId);

            if (uploadArea) {
                displayUploadedImage(uploadArea, uploadId, pilotId, weaponId, weapon.image_data);
            }
        }
    }
}


// Add button to trigger the load function (optional)
function addLoadSubmitDataButton() {
    const header = document.querySelector('.header');
    if (header) {
        const loadButton = document.createElement('button');
        loadButton.textContent = 'Load Submit Data';
        loadButton.className = 'btn-primary';
        loadButton.style.position = 'absolute';
        loadButton.style.right = '20px';
        loadButton.style.top = '50%';
        loadButton.style.transform = 'translateY(-50%)';
        loadButton.onclick = loadFromSubmitDataFile; // Uses file picker version

        header.appendChild(loadButton);
    }
}

// Function to automatically load submit data from URL parameter
async function autoLoadFromURLParameter() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const id = urlParams.get('id');

        if (id) {
            console.log(`Found URL parameter id=${id}, loading submit data...`);

            const response = await fetch(`/debrief-sdata/${id}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch submit data: ${response.status} ${response.statusText}`);
            }

            const submitData = await response.json();
            loadFromSubmitDataJSON(submitData);

            console.log(`Successfully loaded submit data for id=${id}`);
            return submitData;
        }
    } catch (error) {
        console.error('Error auto-loading submit data from URL:', error);
        alert(`Error loading submit data from URL: ${error.message}`);
        throw error;
    }
}

// Function to check URL parameter and auto-load on page load
function initializeAutoLoad() {
    // Check if we should auto-load from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('id')) {
        updateSubmitButtonText()
        // Wait for the page to be fully loaded before auto-loading
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(autoLoadFromURLParameter, 500); // Small delay to ensure everything is initialized
            });
        } else {
        }
    }
}

function showCallsignPopup() {
    const popup = document.getElementById('callsignPopup');
    const closeBtn = document.getElementById('closePopupBtn');
    const callsignSelect = document.getElementById('callsignSelect');
    const loadButton = document.getElementById('loadButton');
    const manualButton = document.getElementById('manualButton');
    const missionDataSelect = document.getElementById('missionDataSelect');

    popup.style.display = 'flex';
    closeBtn.style.display = 'block'; // Show close button when opened via settings

    const hasCallsign = !!callsignSelect.value;
    const hasMissionData = !!missionDataSelect.value;

    loadButton.disabled = !hasCallsign || !hasMissionData;
    manualButton.disabled = !hasCallsign;
}

function validateFileSize(file) {
    const fileType = file.type.split('/')[1].toLowerCase();

    if (fileType === 'gif') {
        const maxFinalSizeBytes = 4 * 1024 * 1024;
        const fileSizeInMB = file.size / (1024 * 1024);
        if (file.size > maxFinalSizeBytes) {
            throw new Error(`GIF file too large (${fileSizeInMB.toFixed(1)}MB). Maximum allowed: 4MB `);
        }
    }
    return true;
}


initializeAutoLoad();

