import './RouteProgress.css'
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import 'nprogress/nprogress.css'
import NProgress from 'nprogress'

NProgress.configure({
    showSpinner: false,
    trickleSpeed: 100,
    minimum: 0.1,
})

function RouteProgress() {
    const location = useLocation()

    useEffect(() => {
        NProgress.start()

        const timer = setTimeout(() => {
            NProgress.done()
        }, 500)

        return () => clearTimeout(timer)
    }, [location.pathname])

    return null
}

export default RouteProgress
