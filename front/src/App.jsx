import './App.css'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Base from "./components/Base.jsx"
import Auth from "./components/Auth.jsx"
import '@ant-design/v5-patch-for-react-19';
import Index from "./components/pages/Index.jsx";


function App() {
    return (
        <>
            <Router>
                <Routes>
                    <Route path="/" element={<Index/>} />
                    {/*<Route path="/search/" element={<Search />} />*/}

                    <Route path="/user/*" element={<Auth/>} />
                    <Route path="/*" element={<Base/>} />
                </Routes>
            </Router>
        </>
    )
}

export default App
