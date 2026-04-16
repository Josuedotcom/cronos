# Cronos - Clarification Questions for Requirements

Durante las fases de **Exploration** y **Proposal**, hemos identificado varios aspectos críticos del negocio que requieren clarificación antes de proceder con diseño y desarrollo.

## 1. Integración de Nómina

**Pregunta:** ¿El sistema debe generar el archivo final de nómina (Novedades de Nómina en formato CSV/XML para Siigo, Novasoft, SAP) O solo exportar las horas categorizadas (ordinarias, nocturnas, extras, recargos) para que HR lo cargue a otro software?

**Impacto:**
- Si es **archivo final:** Necesitamos integración con formatos estándar colombianos + validaciones de totalizados
- Si es **solo exportar horas:** Menos complejidad, pero HR debe manejar el cálculo final en su software de nómina

**Recomendación:** Empezar con exportación de horas categorizadas (MVP), para validar la lógica de cálculo antes de integración completa.

---

## 2. Mecanismo de Reloj (Clock-In/Clock-Out)

**Pregunta:** ¿Cómo se registran las horas reales trabajadas?

**Opciones:**
- A) **Sistema de reloj biométrico** (huella dactilar, facial) integrado con la app
- B) **GPS + Mobile App** (solo para campo)
- C) **Entrada manual por Manager** (HR registra manualmente después de la jornada)
- D) **Combinado** (mayoría manual, biométrico solo en oficina)

**Impacto:**
- Biométrico: Mayor precisión, hardware adicional, costo de integración
- GPS: Mejor para fuerzas móviles/externos
- Manual: Riesgo de fraude, pero flexible
- Combinado: Complejidad intermedia

**Recomendación:** Empezar con **entrada manual por Manager** (MVP) para validar la lógica de cálculo; agregar biométrico en fase 2.

---

## 3. Tolerancia / Períodos de Gracia

**Pregunta:** ¿Cómo se manejan llegadas tempranas / salidas atrasadas?

**Ejemplos:**
- Worker llega 15 min temprano al turno ¿Se cuenta como horas ordinarias o se ignora?
- Worker se va 10 min tarde ¿Se convierte automáticamente en extra o requiere aprobación?

**Impacto:**
- Si es **automático:** Sistema genera automáticamente horas extras (costo payroll)
- Si es **aprobación:** Manager decide caso a caso (más control, pero más carga administrativa)

**Recomendación:** Permitir configurar tolerancia por empresa (ej: +/- 5 min sin efecto, > 5 min requiere aprobación).

---

## 4. Acuerdos Sindicales / Pactos Colectivos

**Pregunta:** ¿Las empresas target tienen **Convenciones Colectivas** (acuerdos sindicales) que modifiquen los porcentajes de CST?

**Ejemplo:**
- CST estándar: Recargo nocturno 35%
- Pacto colectivo: Recargo nocturno 50%

**Impacto:**
- Si sí: Sistema debe permitir configuración por empresa (es crítico para legalidad)
- Si no: Usamos porcentajes estándar del CST

**Recomendación:** Diseñar `surcharge_rules` como **configurables por company + effective_date** para manejar cambios de ley y pactos colectivos.

---

## 5. Modalidad de Turnos Especiales

**Pregunta:** ¿Las empresas usan **turnos sucesivos de 36 horas** (6 horas × 6 días) o solo turnos estándar (8-9 horas)?

**Impacto:**
- **Turnos sucesivos:** Reglas diferentes de cálculo (NO generan recargos nocturnos, solo dominicales)
- **Turnos estándar:** Reglas normales de CST

**Recomendación:** Implementar soporte para ambos (`contract_type: 'standard'` vs `'shift_36h'`).

---

## 6. Dominical/Festivo - Compensatorio vs Surcharge

**Pregunta:** ¿Si un worker trabaja el domingo, prefiere la empresa:
- **Opción A:** Pagar el surcharge (75%) y trabajador sigue trabajando
- **Opción B:** Pagar el surcharge + dar día compensatorio pagado
- **Opción C:** Configurar por empresa

**Nota legal:** Si el domingo es **habitual** (3+ domingos/mes), el worker tiene DERECHO a ambos (surcharge + compensatorio).

**Impacto:** Lógica de cálculo y generación de "días libres" compensatorios.

**Recomendación:** Hacer configurable por empresa.

---

## 7. Multi-Tenancy (Ambición del Proyecto)

**Pregunta:** ¿Es esto para:
- **Una sola empresa** (single-tenant)
- **Múltiples empresas SaaS** (multi-tenant)
- **Futuro SaaS pero por ahora una empresa** (diseñar para multi desde el inicio)

**Impacto:**
- Single-tenant: Modelo más simple (sin column `company_id` en tablas)
- Multi-tenant: Más complejo, pero reutilizable. Requiere row-level security, auditoría, aislamiento de datos

**Recomendación:** **Diseñar multi-tenant desde el inicio** (agregar `company_id` a todas las tablas), pero deploy inicial con una sola empresa (costo/beneficio de desarrollo similar pero futuro-proof).

---

## 8. Analítica y Reportes Específicos

**Pregunta:** ¿Qué reportes específicos necesita HR?

**Ejemplos comunes:**
- Total de horas por tipo (ordinarias, nocturnas, extras, recargos) por período
- Listado de trabajadores con dominicales habituales
- Alertas de límites de horas superados
- Auditoria de cambios de turno
- Comparativo mes anterior vs mes actual

**Impacto:** Define qué vistas/índices necesitamos en BD + endpoints de reportería.

**Recomendación:** Empezar con reportes básicos (totales por tipo), agregar avanzados post-MVP.

---

## 9. Autenticación / SSO

**Pregunta:** ¿Las empresas usan:
- **Credential local** (usuario/contraseña en la app)
- **SSO integrado** (Active Directory, Azure AD, Google Workspace)
- **Ambas opciones**

**Impacto:** Decide si implementamos JWT local o OAuth2/OIDC.

**Recomendación:** Empezar con JWT local (MVP), agregar SSO en fase 2.

---

## 10. Movilidad (Web vs Mobile)

**Pregunta:** ¿Los workers acceden desde:
- **Web (escritorio/laptop)** - view-only
- **Mobile (iOS/Android)** - view-only + ability to request swaps
- **Ambos**

**Impacto:** Define si necesitamos app nativa (Flutter/React Native) o PWA.

**Recomendación:** Empezar con **web responsive** (Vite + React), hacer PWA compatible con mobile. App nativa post-MVP si es necesario.

---

## 11. Notificaciones en Tiempo Real

**Pregunta:** ¿Se necesitan notificaciones push (real-time) para:
- Cambios de turno asignados
- Swap requests (cuando alguien pide cambiar turno contigo)
- Aprobaciones de swaps
- Recargos detectados (alertas)

**Impacto:**
- Si sí: WebSocket + Celery task queue + Redis
- Si no: Email/SMS suficiente (más simple)

**Recomendación:** MVP con email, agregar push en fase 2 si es crítico.

---

## 12. Períodos de Migración / Histórico

**Pregunta:** ¿Hay datos históricos de turnos/nómina de un sistema anterior?

**Impacto:**
- Si sí: Necesitamos script de migración + validación de datos
- Si no: Empezamos en blanco

**Recomendación:** Validar datos históricos si existen.

---

## Próximos Pasos

**Por favor responde las preguntas anteriores** (mínimo: 1, 2, 3, 4, 6, 7) para que podamos:

1. ✅ **Proposal Phase:** Alinear scope y features
2. ✅ **Spec Phase:** Definir requerimientos precisos
3. ✅ **Design Phase:** Arquitectura final
4. ✅ **Apply Phase:** Comenzar implementación

---

**Nota:** Estas preguntas son derivadas de la exploración del dominio colombiano. Responderlas nos permite diseñar un sistema robusto y cumplidor desde el inicio.
