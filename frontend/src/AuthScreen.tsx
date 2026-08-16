import { FormEvent, useState } from "react";
import {
  loginAccount,
  registerAccount,
  setAuthToken,
  type AuthStatus,
} from "./services/api";

type AuthScreenProps = {
  onReady: (status: AuthStatus) => void;
};

export function AuthScreen({ onReady }: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const session =
        mode === "register"
          ? await registerAccount(email, password, name)
          : await loginAccount(email, password);
      setAuthToken(session.token);
      onReady({
        auth_required: true,
        user: session.user,
        profile_id: session.user.profile_id,
      });
    } catch (nextError) {
      setError((nextError as Error).message.replace(/^API \d+: /, ""));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="authShell">
      <a className="skip" href="#auth-form">
        Saltar al formulario
      </a>
      <section className="authCard" id="auth-form">
        <p className="brandWord">Editados</p>
        <h1>{mode === "login" ? "Entra a tu cuenta" : "Crea tu cuenta"}</h1>
        <p>
          Cada persona tiene su criterio, su historial y sus textos. Nadie más
          los ve.
        </p>
        <form className="authForm" onSubmit={handleSubmit}>
          {mode === "register" ? (
            <label>
              Nombre
              <input
                autoComplete="name"
                onChange={(event) => setName(event.target.value)}
                value={name}
              />
            </label>
          ) : null}
          <label>
            Correo
            <input
              autoComplete="email"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </label>
          <label>
            Contraseña
            <input
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button className="primaryButton" disabled={busy} type="submit">
            {busy ? "Un momento…" : mode === "login" ? "Entrar" : "Crear cuenta"}
          </button>
        </form>
        <button
          className="textButton"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          type="button"
        >
          {mode === "login" ? "No tengo cuenta" : "Ya tengo cuenta"}
        </button>
      </section>
    </main>
  );
}
