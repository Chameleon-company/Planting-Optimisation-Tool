import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useStickyHeader } from "@/hooks/useStickyHeader";
import "../../style.css";

export default function MainLayout() {
  const { isScrolled } = useStickyHeader();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const isHome = pathname === "/";

  return (
    <>
      <header
        className={`topbar ${isHome ? "home-topbar" : ""} ${isScrolled ? "is-scrolled" : ""}`}
      >
        <div className="topbar-inner">
          <div className="brand">
            <img
              src="/assets/images/logo2.svg"
              alt="Logo"
              className="aboutLogo"
            />
          </div>
          <nav className="nav">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              Environmental Profile
            </NavLink>
            <NavLink
              to="/calculator"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              Sapling Calculator
            </NavLink>
            <NavLink
              to="/recommendation"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              Agroforestry Recommendation
            </NavLink>
            <NavLink
              to="/species"
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
            >
              Species
            </NavLink>
          </nav>
          <div className="actions">
            {user ? (
              <div className="user-info">
                <span>Welcome, {user.name}</span>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </div>
            ) : (
              <div className="auth-actions">
                <NavLink to="/login" className="login-btn">
                  Login
                </NavLink>
                <NavLink to="/register" className="login-btn">
                  Register
                </NavLink>
              </div>
            )}
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-col footer-brand">
            <img
              src="/assets/images/logo2.svg"
              alt="Logo"
              className="aboutLogo"
            />
            <div className="product">
              <div className="product-title">Planting Optimisation Tool</div>
              <p className="product-desc">
                The tool helps farmers and agronomists optimise farm species,
                soil, and sapling recommendations for maximum yield and
                sustainability.
              </p>
            </div>
          </div>
          <div className="footer-col">
            <div className="footer-heading">Explore</div>
            <ul className="footer-links">
              <li>
                <NavLink to="/">Home</NavLink>
              </li>
              <li>
                <NavLink to="/profile">Environmental Profile</NavLink>
              </li>
              <li>
                <NavLink to="/calculator">Sapling Calculator</NavLink>
              </li>
              <li>
                <NavLink to="/recommendation">
                  Agroforestry Recommendation
                </NavLink>
              </li>
              <li>
                <NavLink to="/species">Species</NavLink>
              </li>
            </ul>
          </div>
        </div>
      </footer>
    </>
  );
}
