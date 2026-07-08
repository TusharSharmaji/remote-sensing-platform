import { Outlet } from "react-router-dom";

function MainLayout() {
  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "system-ui",
      }}
    >
      <h1>🚀 Remote Sensing Platform</h1>

      <Outlet />
    </div>
  );
}

export default MainLayout;