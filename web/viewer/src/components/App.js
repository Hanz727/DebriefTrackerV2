import '../App.css';
import Header from "./Header";
import Body from "./Body";
import Sidebar from "./Sidebar";

function App() {
    return (
        <div className="App">
            <Sidebar/>
            <Header/>
            <Body/>
        </div>
    );
}

export default App;
