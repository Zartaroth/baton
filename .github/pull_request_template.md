## Qué cambia y por qué

<!-- El motivo importa tanto como el cambio (principio 6). Enlaza el issue o la discusión: "Closes #123". -->

## Tipo

- [ ] Corrección (baton.py, skills, plantillas)
- [ ] Mejora o skill nueva
- [ ] Cambio a la metodología o a un formato (discutido antes en #)
- [ ] Documentación o traducción

## Revisión

- [ ] `bash pruebas/e2e.sh` termina en "todo ok"
- [ ] Si arreglé un error, agregué a la prueba el caso que lo reproduce
- [ ] Si cambié un formato, actualicé FORMATOS.md, baton.py, las plantillas y las skills afectadas, y subí `formato` si el cambio rompe compatibilidad
- [ ] No rompe ninguna invariante de METODOLOGIA.md
- [ ] Agregué una entrada en CHANGELOG.md si el cambio afecta a quien usa Baton
