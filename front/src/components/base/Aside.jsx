import './Aside.css'
import {
    Back,
    Bookmark,
    Cancel,
    Collections,
    Film,
    Home,
    Later,
    Like,
    Random,
    Series,
    Watch
} from "../../icons/icons.jsx";
import {useEffect, useState} from "react";
import axios from "axios";
import {Link} from "react-router-dom";
import {Button} from "antd";

function Aside({ isOpen, setIsOpen }) {
    const [socials, setSocials] = useState([]);
    const [random, setRandom] = useState([]);

    useEffect(() => {
        const cached = localStorage.getItem('socials');

        axios.get('http://localhost:8080/random_media/')
            .then(res => setRandom(res.data))
            .catch(error => console.error('Ошибка при запросе:', error));

        if (cached) {
            setSocials(JSON.parse(cached));
        } else {
            axios.get('http://localhost:8080/statify/social/api/list/')
                .then(response => {
                    setSocials(response.data.socials);
                    localStorage.setItem('socials', JSON.stringify(response.data.socials));
                })
                .catch(error => console.error('Ошибка при запросе:', error));
        }
    }, [])

    return (
        <aside className={isOpen ? 'aside active' : 'aside'} id="Aside">
            <Button
                className="hide-aside-btn"
                icon={<Back style={{ width: "15px", height: "auto" }} />}
                onClick={() => {setIsOpen(false)}}
            >
                Назад
            </Button>

            <section className="aside-block aside-pages">
                <Link to="/" className="aside-link">
                    <Home/>

                    <span>Главная</span>
                </Link>

                <Link to="/collections" className="aside-link">
                    <Collections/>

                    <span>Подборки</span>
                </Link>
            </section>

            <section className="aside-block">
                <Link className="aside-link" to="/profile/media_status/favorites">
                    <Like/>

                    <span>Избранное</span>
                </Link>

                <Link className="aside-link" to="/profile/media_status/watching">
                    <Watch/>

                    <span>Смотрю</span>
                </Link>
                <Link className="aside-link" to="/profile/media_status/watch_later">
                    <Later/>

                    <span>На потом</span>
                </Link>
                <Link className="aside-link" to="/profile/media_status/bookmarks">
                    <Bookmark/>

                    <span>Закладки</span>
                </Link>
                <Link className="aside-link" to="/profile/media_status/dropped">
                    <Cancel/>

                    <span>Брошенные</span>
                </Link>
            </section>

            <section className="aside-block random-media" id="asideRandom">
                {(
                    <a className="aside-link" href={random.url} title='Случайная дорама'>
                        <Random/>

                        <span>Случайная дорама</span>
                    </a>
                )}
            </section>

            <section className="aside-block aside-community" id="asideCommunity">
                {socials.map((social, i) => (
                    <a
                        key={i}
                        className="aside-link"
                        title={social.name}
                        href={social.url}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <span className="aside-block-svg-cont" dangerouslySetInnerHTML={{ __html: social.icon_svg }} />
                        <span>{social.name}</span>
                    </a>
                ))}
            </section>
        </aside>
    )
}

export default Aside;

export function handleAside(setIsAsideOpen) {
    setIsAsideOpen(prev => !prev);
}