import React from "react";
import '../Filters.css'

const Filters = ({refreshFunc}) => {
    const refresh = () => {
        refreshFunc();
    }

    return (
        <div className="App-Filters">
            <div className="Filter">
                <label htmlFor="pilot">Pilot</label>
                <input type="text" className="PilotFilter" id="pilot" onInput={refresh}/>
            </div>

            <div className="Filter">
                <label htmlFor="rio">Rio</label>
                <input type="text" className="RioFilter" id="rio" onInput={refresh}/>
            </div>

            <div className="Filter">
                <label htmlFor="modex">Tail number</label>
                <input type="number" className="ModexFilter" id="modex" onInput={refresh}/>
            </div>

            <div className="Filter">
                <label htmlFor="target">Target</label>
                <input type="text" className="TargetFilter" id="target" onInput={refresh}/>
            </div>

            <datalist id="weaponTypes">
                <option value="A/A" />
                <option value="A/G" />
                <option value="N/A" />
            </datalist>

            <div className="Filter">
                <label htmlFor="weapon_type">Weapon type</label>
                <input type="text" list="weaponTypes" className="WeaponTypeFilter" id="weapon_type" onInput={refresh}/>
            </div>

            <div className="Filter">
                <label htmlFor="weapon">Weapon</label>
                <input type="text" className="WeaponFilter" id="weapon" onInput={refresh}/>
            </div>

            <datalist id="bool">
                <option value="TRUE" />
                <option value="FALSE" />
            </datalist>

            <div className="Filter">
                <label htmlFor="killed">Hit?</label>
                <input type="text" list="bool" className="KilledFilter" id="killed" onInput={refresh}/>
            </div>

        </div>
    )
}

export default Filters