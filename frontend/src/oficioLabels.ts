import type { OficioFichaData } from "./types/api";

export const ramas: Array<{ id: OficioFichaData["rama"] | "todas"; label: string }> = [
  { id: "todas", label: "Todas" },
  { id: "lengua", label: "La lengua como material" },
  { id: "recursos", label: "Recursos expresivos" },
  { id: "composicion", label: "Composición" },
  { id: "voz", label: "Voz y estilo" },
  { id: "generos", label: "Géneros" },
  { id: "tradicion", label: "Tradición" },
  { id: "criterio", label: "Proceso y criterio" },
];

export const accionLabels: Record<string, string> = {
  correction: "Corregir",
  rewrite: "Editar",
  sendable: "Hacer enviable",
  review: "Revisar por bloques",
  read: "Leer con fichas",
  continue: "Continuar",
  variants: "Variantes",
};

export const miradaLabels: Record<string, string> = {
  comprension: "comprensión",
  estructura: "estructura",
  tono: "tono",
  limpieza: "limpieza",
};

export const metricaLabels: Record<string, string> = {
  frase_larga: "frases muy largas",
  repeticion_cercana: "palabras repetidas muy cerca",
  anafora: "frases seguidas que empiezan igual",
  deriva_estilo: "cambio de ritmo entre el principio y el final",
  parrafo_largo: "párrafos muy largos",
  bloque_unico: "todo el texto en un solo bloque",
  ques_encadenados: "muchos «que» en una frase",
  des_encadenados: "cadenas de «de»",
  mente_encadenados: "varios adverbios en -mente",
  eco_sufijos: "terminaciones repetidas (-ción, -mente…)",
  intensificadores: "muchos intensificadores",
  frases_cortas: "muchas frases muy cortas seguidas",
  trato_mixto: "trato de tú y de usted mezclado",
  incisos: "frases con muchos incisos",
};

export const relacionLabels: Record<string, string> = {
  prioridad_sobre: "Prevalece sobre",
  conflicto_con: "Choca con",
  requiere: "Requiere",
};

export const propuestaTipoLabels: Record<string, string> = {
  revisar: "Revisar la ficha",
  acotar_senal: "Acotar la señal",
  anadir_senal: "Añadir una señal",
  crear: "Ficha nueva",
};

export const campoLabels: Record<keyof OficioFichaData, string> = {
  id: "Identificador",
  rama: "Rama",
  nombre: "Nombre",
  regla: "Regla",
  aplica: "Aplica",
  no_aplica: "No aplica",
  ejemplos: "Ejemplos",
  fuente: "Fuente",
  senales: "Señales",
  metricas: "Métricas",
  base: "Base",
  generos: "Géneros",
  relaciones: "Relaciones",
  protege: "Protege el sentido",
};

export function ramaLabel(rama: string) {
  return ramas.find((item) => item.id === rama)?.label ?? rama;
}

export function normalize(value: string) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "");
}

export function slugify(value: string) {
  return normalize(value)
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
}

export function emptyFicha(): OficioFichaData {
  return {
    id: "",
    rama: "composicion",
    nombre: "",
    regla: "",
    aplica: "",
    no_aplica: "",
    ejemplos: [{ mal: "", bien: "", porque: "" }],
    fuente: { obra: "Criterio de Editados", localizador: "" },
    senales: [],
    metricas: [],
    base: { acciones: [], miradas: [] },
    generos: [],
    relaciones: [],
    protege: false,
  };
}

/** Texto legible de un campo para comparar versiones. */
export function fieldText(ficha: OficioFichaData | null, field: keyof OficioFichaData): string {
  if (!ficha) return "";
  const value = ficha[field];
  switch (field) {
    case "ejemplos":
      return ficha.ejemplos.map((item) => `✗ ${item.mal}\n✓ ${item.bien}\n  ${item.porque}`).join("\n\n");
    case "fuente":
      return `${ficha.fuente.obra} · ${ficha.fuente.localizador}`;
    case "senales":
      return ficha.senales
        .map((item) => `${item.tipo === "vigilancia" ? "[vigilancia]" : "[error]"} ${item.patron}`)
        .join("\n");
    case "metricas":
      return ficha.metricas.map((item) => metricaLabels[item] ?? item).join(", ");
    case "base":
      return [
        ficha.base.acciones.map((item) => accionLabels[item] ?? item).join(", "),
        ficha.base.miradas.map((item) => miradaLabels[item] ?? item).join(", "),
      ]
        .filter(Boolean)
        .join(" · ");
    case "generos":
      return ficha.generos.join(", ");
    case "relaciones":
      return ficha.relaciones
        .map((item) => `${relacionLabels[item.tipo]} ${item.ficha}${item.criterio ? ` — ${item.criterio}` : ""}`)
        .join("\n");
    case "protege":
      return ficha.protege ? "Sí" : "No";
    default:
      return String(value ?? "");
  }
}
