import './Codes.css'
import {Link} from "react-router-dom";

function NotFound() {
    return (
        <section className="main-block codes-block">
            <h1>Ошибка 404 — Страница не найдена</h1>
            <p>Извините, страница, которую вы ищете, не существует или была удалена.</p>
            <p>Проверьте адрес или вернитесь на главную страницу.</p>
            <p>Если вы думаете, что это ошибка, <Link to="/support">напишите в поддержку</Link>.</p>
            <Link to="/">Вернуться на главную</Link>
        </section>
    )
}

export default NotFound;